import axios from 'axios'
const uuidv4 = require('uuid/v4')

const ILLUSIONIST_PORT = process.env.VUE_APP_ILLUSIONIST_PORT
const LUKE_URL = process.env.VUE_APP_LUKE_URL

const illusionistAPI = axios.create({
  headers: {
    'content-type': 'application/json',
    'Access-Control-Allow-Origin': '*'
  },
  baseURL: 'http://' + window.location.hostname + ':' + ILLUSIONIST_PORT
})

illusionistAPI.interceptors.request.use(function (config) {
  const token = window.localStorage.getItem('access_token')
  if (!config.headers) {
    config.headers = {}
  }
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

const lukeAPI = axios.create({
  headers: {
    'content-type': 'application/json'
  },
  baseURL: LUKE_URL
})

lukeAPI.interceptors.request.use(function (config) {
  const token = window.localStorage.getItem('access_token')
  if (!config.headers) {
    config.headers = {}
  }
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

const apiPathSid = function (path, sessionId) {
  if (sessionId === '') {
    sessionId = uuidv4()
  }

  var apiPath = path + '?session_id=' + sessionId
  return apiPath
}
export { illusionistAPI, lukeAPI, apiPathSid }
