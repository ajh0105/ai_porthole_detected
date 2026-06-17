import api from './axiosInstance'
import { IS_DEMO, mockRoadDamageApi } from './mockData'

export const roadDamageApi = {
  getList:     (params) => IS_DEMO ? mockRoadDamageApi.getList(params)  : api.get('/road-damage', { params }),
  getOne:      (id)     => IS_DEMO ? mockRoadDamageApi.getOne(id)       : api.get(`/road-damage/${id}`),
  getMapData:  (bbox)   => IS_DEMO ? mockRoadDamageApi.getMapData(bbox) : api.get('/road-damage/map', {
    params: { minLng: bbox[0], minLat: bbox[1], maxLng: bbox[2], maxLat: bbox[3] },
  }),
  getStats:    ()       => IS_DEMO ? mockRoadDamageApi.getStats()        : api.get('/road-damage/stats'),
  getDistricts: ()      => IS_DEMO ? mockRoadDamageApi.getDistricts()    : api.get('/road-damage/districts'),
  upload: (files) => {
    if (IS_DEMO) return Promise.reject(Object.assign(new Error('DEMO_MODE'), { isDemoMode: true }))
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    return api.post('/road-damage/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  delete: (id) => {
    if (IS_DEMO) return Promise.reject(Object.assign(new Error('DEMO_MODE'), { isDemoMode: true }))
    return api.delete(`/road-damage/${id}`)
  },
}
