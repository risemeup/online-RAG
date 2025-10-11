import axios from 'axios'
import { API_BASE_URL, REQUEST_TIMEOUT } from './config'
import { ElMessage } from 'element-plus'

// 定义API响应格式接口
interface APIResponse<T = any> {
  code: number
  msg: string
  data: T
}

// 创建实例
const service = axios.create({
  baseURL: API_BASE_URL, // 基础路径
  timeout: REQUEST_TIMEOUT // 超时时间
})

// 响应拦截器（处理错误等）
service.interceptors.response.use(
  response => {
    const apiResponse: APIResponse = response.data
    
    // 检查业务状态码
    if (apiResponse.code !== 0) {
      // 业务错误，显示错误消息
      ElMessage.error(apiResponse.msg || '请求失败')
      return Promise.reject(new Error(apiResponse.msg || '请求失败'))
    }
    
    // 成功时返回data字段
    return apiResponse.data
  },
  error => {
    // 网络错误或其他HTTP错误
    console.error('请求错误:', error)
    
    let errorMessage = '网络请求失败'
    if (error.response) {
      // 服务器返回了错误状态码
      errorMessage = `请求失败: ${error.response.status}`
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '网络连接失败，请检查网络'
    } else {
      // 其他错误
      errorMessage = error.message || '未知错误'
    }
    
    ElMessage.error(errorMessage)
    return Promise.reject(error)
  }
)

export default service