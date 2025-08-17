const APP_PREFIX = 'WEB'
const USER_KEY = `${APP_PREFIX}_USER`
function tokenKey(uid) { return `${APP_PREFIX}_TOKEN:${uid || 'ANON'}` }
function tokenExpKey(uid) { return `${APP_PREFIX}_TOKEN_EXPIRES_AT:${uid || 'ANON'}` }

export function setToken(token, expiresAt) {
  const uid = getUserId() || 'ANON'
  localStorage.setItem(tokenKey(uid), token)
  if (expiresAt) localStorage.setItem(tokenExpKey(uid), expiresAt)
}

export function getToken() {
  const uid = getUserId() || 'ANON'
  return localStorage.getItem(tokenKey(uid)) || ''
}

export function clearToken() {
  const uid = getUserId() || 'ANON'
  localStorage.removeItem(tokenKey(uid))
  localStorage.removeItem(tokenExpKey(uid))
}

export function setUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user || {}))
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || '{}')
  } catch (e) {
    return {}
  }
}

export function getUserId() {
  const u = getUser()
  return u && u.user_id ? u.user_id : null
}

export function clearUser() {
  localStorage.removeItem(USER_KEY)
}

export default {
  setToken,
  getToken,
  clearToken,
  setUser,
  getUser,
  clearUser
}


