import api from './axiosInstance'
import { IS_DEMO, mockBlackIceApi } from './mockData'

export const blackIceApi = {
  getList:         (params) => IS_DEMO ? mockBlackIceApi.getList(params)           : api.get('/blackice', { params }),
  getMapData:      (bbox)   => IS_DEMO ? mockBlackIceApi.getMapData(bbox)          : api.get('/blackice/map', {
    params: { minLng: bbox[0], minLat: bbox[1], maxLng: bbox[2], maxLat: bbox[3] },
  }),
  getStats:        ()       => IS_DEMO ? mockBlackIceApi.getStats()                : api.get('/blackice/stats'),
  getStations:     ()       => IS_DEMO ? mockBlackIceApi.getStations()             : api.get('/blackice/stations'),
  getCurrentWeather: ()     => IS_DEMO ? mockBlackIceApi.getCurrentWeather()       : api.get('/blackice/current-weather'),
  getRegionWeather: (lat, lng) => IS_DEMO
    ? mockBlackIceApi.getRegionWeather(lat, lng)
    : api.get('/blackice/region-weather', { params: { lat, lng } }),
  predict: () => {
    if (IS_DEMO) return Promise.reject(Object.assign(new Error('DEMO_MODE'), { isDemoMode: true }))
    return api.post('/blackice/predict')
  },
}
