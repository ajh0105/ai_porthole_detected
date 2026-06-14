import api from './axiosInstance'

export const roadDamageApi = {
  getList: (params) => api.get('/road-damage', { params }),
  getOne: (id) => api.get(`/road-damage/${id}`),
  getMapData: (bbox) => api.get('/road-damage/map', {
    params: { minLng: bbox[0], minLat: bbox[1], maxLng: bbox[2], maxLat: bbox[3] }
  }),
  getStats: () => api.get('/road-damage/stats'),
  upload: (files) => {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    return api.post('/road-damage/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  delete: (id) => api.delete(`/road-damage/${id}`),
  getDistricts: () => api.get('/road-damage/districts'),
}
