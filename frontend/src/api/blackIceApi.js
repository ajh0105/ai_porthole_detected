import api from './axiosInstance'

export const blackIceApi = {
  getList: (params) => api.get('/blackice', { params }),
  getMapData: (bbox) => api.get('/blackice/map', {
    params: { minLng: bbox[0], minLat: bbox[1], maxLng: bbox[2], maxLat: bbox[3] }
  }),
  getStats: () => api.get('/blackice/stats'),
  predict: () => api.post('/blackice/predict'),
  getStations: () => api.get('/blackice/stations'),
  getRegionWeather: (lat, lng) => api.get('/blackice/region-weather', { params: { lat, lng } }),
  getCurrentWeather: () => api.get('/blackice/current-weather'),
}
