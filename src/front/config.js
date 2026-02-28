const CONFIG = {
    API_BASE_URL: 'http://localhost:5000',
    API_ENDPOINTS: {
        SCL90_QUESTIONS: '/api/scl90/questions',
        SCL90_SUBMIT: '/api/scl90/submit',
        SCL90_HISTORY: '/api/scl90/history',
        SCL90_DETAIL: '/api/scl90/detail',
        MENTAL_ANALYSIS: '/api/mental_analysis',
        DIALOGUE_HISTORY: '/api/dialogue/history',
        KNOWLEDGE_ADD: '/api/knowledge/add',
        KNOWLEDGE_LIST: '/api/knowledge/list',
        KNOWLEDGE_DELETE: '/api/knowledge/delete',
        KNOWLEDGE_DETAIL: '/api/knowledge/detail',
        SESSIONS: '/api/sessions',
        SESSION_MESSAGES: '/api/sessions',
        SESSION_DELETE: '/api/sessions',
    },
    TIMEOUT: 30000,
    RETRY_COUNT: 3,
};

function getApiUrl(endpoint, ...params) {
    let url = CONFIG.API_BASE_URL + CONFIG.API_ENDPOINTS[endpoint];
    params.forEach(param => {
        url = url.replace(/\/$/, '') + '/' + param;
    });
    return url;
}

async function apiRequest(endpoint, paramOrOptions, options = {}) {
    let url;
    let finalOptions;
    
    if (typeof paramOrOptions === 'object' && paramOrOptions !== null && !Array.isArray(paramOrOptions)) {
        url = typeof endpoint === 'string' && endpoint.startsWith('http') 
            ? endpoint 
            : getApiUrl(endpoint);
        finalOptions = paramOrOptions;
    } else {
        url = typeof endpoint === 'string' && endpoint.startsWith('http') 
            ? endpoint 
            : getApiUrl(endpoint, paramOrOptions);
        finalOptions = options;
    }
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const uuid = window.UUIDManager ? window.UUIDManager.getUUID() : null;
    if (uuid) {
        defaultOptions.headers['X-User-UUID'] = uuid;
    }
    
    const mergedOptions = {
        ...defaultOptions,
        ...finalOptions,
        headers: {
            ...defaultOptions.headers,
            ...finalOptions.headers,
        },
    };
    
    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.msg || `HTTP Error: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

window.AppConfig = {
    ...CONFIG,
    getApiUrl,
    apiRequest,
};
