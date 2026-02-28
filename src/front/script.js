// 全局变量

// 格式化用时函数（全局可用）
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    let result = '';
    if (hours > 0) result += `${hours}小时`;
    if (minutes > 0) result += `${minutes}分钟`;
    result += `${secs}秒`;
    return result;
}

let currentQuestionIndex = 0;
let answers = [];
let startTime = null;
let timerInterval = null;
let timeLeft = 45 * 60; // 45分钟
let userInfo = {};
let testStartTime = null;
let scl90Questions = []; // 从后端获取

// DOM元素
const startScreen = document.getElementById('start-screen');
const testScreen = document.getElementById('test-screen');
const resultScreen = document.getElementById('result-screen');
const historyScreen = document.getElementById('history-screen');
const userInfoForm = document.getElementById('user-info-form');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const questionText = document.getElementById('question-text');
const options = document.querySelectorAll('.option-pill input[type="radio"]');
const currentQuestionEl = document.getElementById('current-question');
const remainingQuestionsEl = document.getElementById('remaining-questions');
const progressFill = document.getElementById('progress-fill');
const timeLeftEl = document.getElementById('time-left');
const themeToggleBtn = document.getElementById('theme-toggle');
const downloadPdfBtn = document.getElementById('download-pdf');
const downloadImageBtn = document.getElementById('download-image');
const restartTestBtn = document.getElementById('restart-test');

// 辅助函数：格式化日期
function formatDate(date) {
    if (!(date instanceof Date)) date = new Date(date);
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

// 初始化
window.addEventListener('DOMContentLoaded', async () => {
    // 确保UUID存在
    if (window.UUIDManager) {
        window.UUIDManager.getUUID();
    }

    // 主题切换
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    
    // 检查本地存储的主题设置
    if (localStorage.getItem('theme') === 'dark' || 
        (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.body.classList.add('dark');
    }
    
    // 加载用户数据
    loadUserData();
    
    // 初始化生日选择器
    initBirthdayPicker();
    
    // 尝试恢复上次进度
    loadState();
    
    // 从后端加载题目
    await loadQuestions();

    // 表单提交
    userInfoForm.addEventListener('submit', startTest);
    
    // 查看往期数据按钮
    const viewHistoryBtn = document.getElementById('view-history');
    if (viewHistoryBtn) {
        viewHistoryBtn.addEventListener('click', showHistoryScreen);
    }
    
    const historyBackBtn = document.getElementById('history-back-btn');
    if (historyBackBtn) {
        historyBackBtn.addEventListener('click', () => {
            historyScreen.classList.add('hidden');
            startScreen.classList.remove('hidden');
        });
    }

    const backToHomeBtn = document.getElementById('back-to-home');
    if (backToHomeBtn) {
        backToHomeBtn.addEventListener('click', () => {
            resultScreen.classList.add('hidden');
            startScreen.classList.remove('hidden');
        });
    }

    const backToHistoryBtn = document.getElementById('back-to-history');
    if (backToHistoryBtn) {
        backToHistoryBtn.addEventListener('click', () => {
            // 返回列表时刷新数据
            showHistoryScreen();
        });
    }
    
    // 导航按钮
    prevBtn.addEventListener('click', goToPreviousQuestion);
    nextBtn.addEventListener('click', goToNextQuestion);
    
    // 选项选择
    options.forEach(option => {
        option.addEventListener('change', () => {
            nextBtn.disabled = false;
            options.forEach(opt => {
                const pill = opt.closest('.option-pill');
                if (pill) {
                    if (opt.checked) pill.classList.add('active');
                    else pill.classList.remove('active');
                }
            });
            setTimeout(goToNextQuestion, 300);
        });
    });
    
    // 下载按钮
    if(downloadPdfBtn) downloadPdfBtn.addEventListener('click', downloadPDF);
    if(downloadImageBtn) downloadImageBtn.addEventListener('click', downloadImage);
    if(restartTestBtn) restartTestBtn.addEventListener('click', restartTest);
    
    const saveToKbBtn = document.getElementById('save-to-kb');
    if(saveToKbBtn) saveToKbBtn.addEventListener('click', saveToKnowledgeBase);
});

// 状态持久化
function saveState() {
    try {
        const state = {
            userInfo,
            answers,
            currentQuestionIndex,
            testStartTime: testStartTime ? testStartTime.getTime() : null
        };
        localStorage.setItem('scl90_state', JSON.stringify(state));
    } catch (e) {
        console.error("保存状态失败", e);
    }
}

function loadState() {
    try {
        const saved = localStorage.getItem('scl90_state');
        if (saved) {
            const state = JSON.parse(saved);
            // 简单验证有效性 (例如超过24小时失效)
            if (state.testStartTime && (Date.now() - state.testStartTime > 24 * 3600 * 1000)) {
                localStorage.removeItem('scl90_state');
                return;
            }
            
            // 提示用户是否恢复
            if (confirm("检测到上次未完成的测试，是否继续？")) {
                userInfo = state.userInfo;
                answers = state.answers || [];
                currentQuestionIndex = state.currentQuestionIndex || 0;
                testStartTime = state.testStartTime ? new Date(state.testStartTime) : new Date();
                
                // 恢复界面状态
                document.getElementById('nickname').value = userInfo.nickname || '';
                document.getElementById('birthday').value = userInfo.birthday || '';
                document.getElementById('gender').value = userInfo.gender || '男';
                
                // 直接进入测试界面 (需要在题目加载完成后)
                // 这里设置标记，等待loadQuestions完成后自动跳转
                window.shouldResume = true;
            } else {
                localStorage.removeItem('scl90_state');
            }
        }
    } catch (e) {
        console.error("加载状态失败", e);
        localStorage.removeItem('scl90_state');
    }
}

async function loadQuestions() {
    try {
        const data = await window.AppConfig.apiRequest('SCL90_QUESTIONS');
        if (data.code === 200) {
            scl90Questions = data.data;
            if (window.shouldResume) {
                document.getElementById('start-btn').click(); 
                setTimeout(() => {
                   userInfoForm.dispatchEvent(new Event('submit'));
                }, 500);
            }
        } else {
            alert("题目加载失败：" + data.msg);
        }
    } catch (e) {
        console.error("加载题目出错", e);
        alert("无法连接后端服务，请检查网络或服务器状态");
    }
}

// 开始测试
function startTest(e) {
    e.preventDefault();
    
    const nickname = document.getElementById('nickname').value;
    const birthday = document.getElementById('birthday').value;
    const gender = document.getElementById('gender').value;
    
    if (!scl90Questions || scl90Questions.length === 0) {
        alert('题目数据尚未加载，请稍候或刷新页面。');
        return;
    }
    
    const age = calculateAge(new Date(birthday));
    
    userInfo = {
        nickname,
        birthday,
        gender,
        age,
        startTime: new Date()
    };
    
    saveUserData(userInfo);
    
    if (window.shouldResume && answers.length > 0) {
        // 使用恢复的数据
        console.log("恢复测试进度...");
        window.shouldResume = false; // 重置标记
    } else {
        testStartTime = new Date();
        answers = new Array(scl90Questions.length).fill(null);
    }
    
    document.body.classList.add('starting');
    startScreen.classList.add('starting');
    
    setTimeout(() => {
        startScreen.classList.add('hidden');
        startScreen.classList.remove('starting');
        testScreen.classList.remove('hidden');
        document.body.classList.remove('starting');
        document.body.classList.add('testing');
        
        showQuestion(currentQuestionIndex);
        startTimer();
    }, 600);
}

// 显示题目
function showQuestion(index) {
    if (index < 0 || index >= scl90Questions.length) return;
    
    const question = scl90Questions[index];
    questionText.textContent = `${index + 1}. ${question.text}`;
    
    currentQuestionEl.textContent = `第 ${index + 1} 题`;
    remainingQuestionsEl.textContent = `剩余 ${scl90Questions.length - (index + 1)} 题`;
    
    const progress = ((index) / scl90Questions.length) * 100;
    progressFill.style.width = `${progress}%`;
    
    // 重置选项
    options.forEach(opt => {
        opt.checked = false;
        opt.closest('.option-pill').classList.remove('active');
    });
    
    // 恢复已选答案
    if (answers[index] !== null) {
        const val = answers[index];
        const opt = document.querySelector(`input[name="answer"][value="${val}"]`);
        if (opt) {
            opt.checked = true;
            opt.closest('.option-pill').classList.add('active');
            nextBtn.disabled = false;
        }
    } else {
        nextBtn.disabled = true;
    }
    
    prevBtn.disabled = index === 0;
    nextBtn.textContent = index === scl90Questions.length - 1 ? '提交测评 🏁' : '下一题 →';
}

function goToNextQuestion() {
    const selected = document.querySelector('input[name="answer"]:checked');
    if (!selected && answers[currentQuestionIndex] === null) {
        alert('请选择一个选项');
        return;
    }
    
    if (selected) {
        answers[currentQuestionIndex] = parseInt(selected.value);
        saveState(); // 保存进度
    }
    
    if (currentQuestionIndex < scl90Questions.length - 1) {
        currentQuestionIndex++;
        showQuestion(currentQuestionIndex);
    } else {
        finishTest();
    }
}

function goToPreviousQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        showQuestion(currentQuestionIndex);
    }
}

async function finishTest() {
    clearInterval(timerInterval);
    
    if (nextBtn.disabled) return;
    nextBtn.disabled = true;
    const originalText = nextBtn.textContent;
    nextBtn.textContent = '提交中...';
    
    const answersMap = {};
    scl90Questions.forEach((q, idx) => {
        answersMap[q.id] = answers[idx];
    });
    
    const uuid = window.UUIDManager ? window.UUIDManager.getUUID() : null;
    
    try {
        const data = await window.AppConfig.apiRequest('SCL90_SUBMIT', {
            method: 'POST',
            body: JSON.stringify({
                answers: answersMap,
                uuid: uuid
            })
        });
        
        if (data.code === 200) {
            localStorage.removeItem('scl90_state');
            showResults(data.data);
        } else {
            alert('提交失败: ' + data.msg);
            nextBtn.disabled = false;
            nextBtn.textContent = originalText;
        }
    } catch (e) {
        console.error(e);
        alert('提交出错，请检查网络');
        nextBtn.disabled = false;
        nextBtn.textContent = originalText;
    }
}

// 显示结果 (使用后端返回的数据)
function showResults(data) {
    window.currentResultData = data; // 保存当前结果供其他功能使用
    testScreen.classList.add('hidden');
    resultScreen.classList.remove('hidden');
    document.body.classList.remove('testing');
    
    let testTimeStr = "";
    let durationStr = "";
    
    const backToHistoryBtn = document.getElementById('back-to-history');
    const restartTestBtn = document.getElementById('restart-test');

    if (data.created_at) {
        // History view
        testTimeStr = data.created_at;
        durationStr = "-"; 
        if (backToHistoryBtn) backToHistoryBtn.classList.remove('hidden');
        if (restartTestBtn) restartTestBtn.classList.add('hidden');
    } else {
        // Fresh view
        const endTime = new Date();
        const duration = testStartTime ? Math.floor((endTime - testStartTime) / 1000) : 0;
        testTimeStr = formatDate(endTime);
        durationStr = formatDuration(duration);
        if (backToHistoryBtn) backToHistoryBtn.classList.add('hidden');
        if (restartTestBtn) restartTestBtn.classList.remove('hidden');
    }
    
    document.getElementById('result-nickname').textContent = userInfo.nickname || '-';
    document.getElementById('result-gender').textContent = userInfo.gender || '-';
    document.getElementById('result-age').textContent = userInfo.age || '-';
    document.getElementById('result-duration').textContent = durationStr;
    document.getElementById('result-test-time').textContent = testTimeStr;
    
    document.getElementById('total-score').textContent = data.total_score;
    document.getElementById('average-score').textContent = data.average_score;
    document.getElementById('positive-items').textContent = data.positive_items_count;
    document.getElementById('score-range').textContent = getScoreStatus(data.average_score);
    
    // 渲染因子表格
    const tbody = document.getElementById('symptoms-tbody');
    tbody.innerHTML = '';
    
    // 渲染图表
    renderChart(data.factor_results);
    
    // 填充表格
    Object.values(data.factor_results).forEach(factor => {
        const tr = document.createElement('tr');
        const isRisky = factor.score >= 2;
        tr.innerHTML = `
            <td>${factor.name}</td>
            <td>${factor.raw_score}</td>
            <td><span class="${isRisky ? 'text-danger font-bold' : ''}">${factor.score}</span></td>
            <td>${isRisky ? '⚠️ 需关注' : '正常'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function getScoreStatus(avg) {
    if (avg < 1.5) return "心理健康";
    if (avg < 2.5) return "轻度症状";
    if (avg < 3.5) return "中度症状";
    return "重度症状";
}

// 其他辅助函数保持不变 (calculateAge, initBirthdayPicker, saveUserData, loadUserData, toggleTheme, renderChart, etc.)
// 简化起见，这里假设原有的辅助函数仍然存在或需要保留。
// 我需要把原文件中未修改的辅助函数也放进来。

function calculateAge(birthday) {
    const today = new Date();
    let age = today.getFullYear() - birthday.getFullYear();
    const m = today.getMonth() - birthday.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthday.getDate())) {
        age--;
    }
    return age;
}

// ---------------- 日期选择器逻辑 ----------------
function initBirthdayPicker() {
    const input = document.getElementById('birthday-input');
    const hidden = document.getElementById('birthday');
    const modal = document.getElementById('birthday-modal');
    if (!input || !modal) return;

    let currentDate = new Date(2000, 0, 1); // 默认 2000-01-01
    const daysContainer = document.getElementById('calendar-days');
    const currentMonthYear = document.getElementById('current-month-year');
    
    // 打开模态窗
    input.addEventListener('click', () => {
        modal.style.display = 'flex';
        renderCalendar();
    });
    
    // 关闭模态窗
    modal.querySelector('.modal-close').addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    document.getElementById('cancel-birthday').addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    document.getElementById('confirm-birthday').addEventListener('click', () => {
        const selected = daysContainer.querySelector('.selected');
        if (selected) {
            const day = parseInt(selected.textContent);
            const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
            const dateStr = `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2,'0')}-${day.toString().padStart(2,'0')}`;
            input.value = dateStr;
            hidden.value = dateStr;
            modal.style.display = 'none';
        } else {
            alert("请选择日期");
        }
    });
    
    // 导航按钮
    document.getElementById('prev-year').addEventListener('click', () => {
        currentDate.setFullYear(currentDate.getFullYear() - 1);
        renderCalendar();
    });
    document.getElementById('next-year').addEventListener('click', () => {
        currentDate.setFullYear(currentDate.getFullYear() + 1);
        renderCalendar();
    });
    document.getElementById('prev-month').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });
    document.getElementById('next-month').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });
    
    function renderCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        currentMonthYear.textContent = `${year}年 ${month + 1}月`;
        
        daysContainer.innerHTML = '';
        
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        // 填充空白
        for (let i = 0; i < firstDay; i++) {
            daysContainer.appendChild(document.createElement('div'));
        }
        
        // 填充日期
        for (let i = 1; i <= daysInMonth; i++) {
            const dayDiv = document.createElement('div');
            dayDiv.textContent = i;
            
            // 检查是否是选中日期 (这里简单处理，每次打开默认选中当前currentDate的日)
            if (i === currentDate.getDate()) {
                dayDiv.classList.add('selected');
            }
            
            dayDiv.addEventListener('click', () => {
                daysContainer.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
                dayDiv.classList.add('selected');
                currentDate.setDate(i);
            });
            
            daysContainer.appendChild(dayDiv);
        }
    }
}

function saveUserData(info) {
    localStorage.setItem('user_info', JSON.stringify(info));
}

function loadUserData() {
    const info = localStorage.getItem('user_info');
    if (info) {
        const data = JSON.parse(info);
        document.getElementById('nickname').value = data.nickname || '';
        document.getElementById('gender').value = data.gender || '';
    }
}

function toggleTheme() {
    document.body.classList.toggle('dark');
    const isDark = document.body.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

function startTimer() {
    timeLeft = 45 * 60;
    updateTimerDisplay();
    timerInterval = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();
        if (timeLeft <= 0) {
            finishTest();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const m = Math.floor(timeLeft / 60);
    const s = timeLeft % 60;
    timeLeftEl.textContent = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function renderChart(factors) {
    const ctx = document.getElementById('result-chart');
    if (!ctx) return;
    
    // 销毁旧图表
    const existingChart = Chart.getChart(ctx);
    if (existingChart) existingChart.destroy();
    
    const labels = Object.values(factors).map(f => f.name);
    const data = Object.values(factors).map(f => f.score);
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: '因子均分',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(54, 162, 235)'
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: { display: false },
                    suggestedMin: 0,
                    suggestedMax: 5
                }
            }
        }
    });
}

function downloadPDF() { 
    // 使用 html2canvas 和 jspdf
    const element = document.querySelector('.result-container');
    const opt = {
        margin:       0.5,
        filename:     `SCL90_Report_${new Date().toISOString().slice(0,10)}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2 },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    
    // 简单实现：由于 jspdf.umd 是模块化引入，这里假设全局变量 jspdf
    if (window.jspdf) {
        const { jsPDF } = window.jspdf;
        html2canvas(element).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('p', 'mm', 'a4');
            const imgProps = pdf.getImageProperties(imgData);
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            pdf.save(opt.filename);
        });
    } else {
        alert("PDF生成库未加载");
    }
}

function downloadImage() { 
    const element = document.querySelector('.result-container');
    html2canvas(element).then(canvas => {
        const link = document.createElement('a');
        link.download = `SCL90_Report_${new Date().toISOString().slice(0,10)}.png`;
        link.href = canvas.toDataURL();
        link.click();
    });
}

async function showHistoryScreen() {
    startScreen.classList.add('hidden');
    testScreen.classList.add('hidden');
    resultScreen.classList.add('hidden');
    historyScreen.classList.remove('hidden');
    
    const tbody = document.getElementById('history-tbody');
    tbody.innerHTML = '<tr><td colspan="4" class="text-center">加载中...</td></tr>';
    
    try {
        const data = await window.AppConfig.apiRequest('SCL90_HISTORY');
        
        tbody.innerHTML = '';
        if (data.code === 200 && data.data.length > 0) {
            data.data.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${item.created_at}</td>
                    <td>${item.total_score}</td>
                    <td>${item.average_score || '-'}</td>
                    <td><button class="btn small secondary" onclick="viewHistoryDetail(${item.id})">查看详情</button></td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">暂无记录</td></tr>';
        }
    } catch (e) {
        console.error(e);
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-danger">加载失败</td></tr>';
    }
}

window.viewHistoryDetail = async function(id) {
    try {
        const data = await window.AppConfig.apiRequest(`SCL90_DETAIL/${id}`);
        
        if (data.code === 200) {
            historyScreen.classList.add('hidden');
            showResults(data.data);
        } else {
            alert(data.msg);
        }
    } catch (e) {
        console.error(e);
        alert("加载详情失败");
    }
};

function restartTest() { location.reload(); }

async function saveToKnowledgeBase() {
    if (!window.currentResultData) {
        alert("暂无测评结果可保存");
        return;
    }
    
    const data = window.currentResultData;
    const dateStr = formatDate(new Date());
    const title = `SCL-90 测评结果 (${dateStr})`;
    
    let content = `测评时间：${dateStr}\n`;
    content += `总分：${data.total_score}，均分：${data.average_score}\n`;
    content += `阳性项目数：${data.positive_items_count}\n`;
    content += `结果判定：${getScoreStatus(data.average_score)}\n\n`;
    
    content += `【因子得分】\n`;
    let riskyFactors = [];
    Object.values(data.factor_results).forEach(f => {
        content += `- ${f.name}: ${f.score} ${f.score >= 2 ? '(⚠️)' : ''}\n`;
        if (f.score >= 2) riskyFactors.push(f.name);
    });
    
    if (riskyFactors.length > 0) {
        content += `\n【需关注症状】\n${riskyFactors.join('、')}\n`;
    } else {
        content += `\n【总体评价】\n心理状态良好，继续保持。\n`;
    }
    
    if (confirm(`确定将结果保存至个人知识库吗？\n标题：${title}`)) {
        try {
            const resData = await window.AppConfig.apiRequest('KNOWLEDGE_ADD', {
                method: 'POST',
                body: JSON.stringify({
                    title: title,
                    content: content,
                    type: 'private'
                })
            });
            if (resData.code === 200) {
                alert("保存成功！您可以在心理咨询页面的个人知识库中查看。");
            } else {
                alert("保存失败：" + resData.msg);
            }
        } catch (e) {
            console.error(e);
            alert("保存出错");
        }
    }
}
