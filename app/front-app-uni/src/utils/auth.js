const APP_PREFIX = 'APP'
const USER_KEY = `${APP_PREFIX}_USER`

function tokenKey(uid) {
	return `${APP_PREFIX}_TOKEN:${uid || 'ANON'}`
}

function tokenExpKey(uid) {
	return `${APP_PREFIX}_TOKEN_EXPIRES_AT:${uid || 'ANON'}`
}

// 安全的存储操作函数
function safeSetStorage(key, value) {
	try {
		uni.setStorageSync(key, value)
	} catch (e) {
		console.warn('设置存储失败:', e)
	}
}

function safeGetStorage(key, defaultValue = '') {
	try {
		return uni.getStorageSync(key) || defaultValue
	} catch (e) {
		console.warn('获取存储失败:', e)
		return defaultValue
	}
}

function safeRemoveStorage(key) {
	try {
		uni.removeStorageSync(key)
	} catch (e) {
		console.warn('删除存储失败:', e)
	}
}

export function setToken(token, expiresAt) {
	const uid = getUserId() || 'ANON'
	safeSetStorage(tokenKey(uid), token)
	if (expiresAt) safeSetStorage(tokenExpKey(uid), expiresAt)
}

export function getToken() {
	const uid = getUserId() || 'ANON'
	return safeGetStorage(tokenKey(uid), '')
}

export function clearToken() {
	const uid = getUserId() || 'ANON'
	safeRemoveStorage(tokenKey(uid))
	safeRemoveStorage(tokenExpKey(uid))
}

export function setUser(user) {
	safeSetStorage(USER_KEY, JSON.stringify(user || {}))
}

export function getUser() {
	try {
		const userStr = safeGetStorage(USER_KEY, '{}')
		return JSON.parse(userStr)
	} catch (e) {
		console.warn('解析用户信息失败:', e)
		return {}
	}
}

export function getUserId() {
	const u = getUser()
	return u && u.user_id ? u.user_id : null
}

export function clearUser() {
	safeRemoveStorage(USER_KEY)
}

export default {
	setToken,
	getToken,
	clearToken,
	setUser,
	getUser,
	clearUser
}