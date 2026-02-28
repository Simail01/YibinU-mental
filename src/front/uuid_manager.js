// UUID管理器
const UUIDManager = {
    // 获取UUID，如果不存在则生成
    getUUID: function() {
        let uuid = localStorage.getItem('yibinu_uuid');
        if (!uuid) {
            uuid = this.generateUUID();
            localStorage.setItem('yibinu_uuid', uuid);
        }
        return uuid;
    },

    // 生成UUID (v4)
    generateUUID: function() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    // 清除UUID及相关数据
    clearData: function() {
        const uuid = this.getUUID();
        // 调用后端清除接口 (可选)
        // fetch('/api/user/clear', { method: 'POST', headers: {'X-User-UUID': uuid} });
        localStorage.removeItem('yibinu_uuid');
        localStorage.clear(); // 清除所有本地缓存
        location.reload();
    }
};

// 导出供其他脚本使用 (如果使用模块化)
// export default UUIDManager;
// 简单环境下直接挂载到window
window.UUIDManager = UUIDManager;
