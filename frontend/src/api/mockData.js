export const IS_DEMO = import.meta.env.VITE_DEMO_MODE === 'true'

export const MOCK_STATIONS = [
  { stationId: '108', stationName: '서울', region: '서울특별시', lat: 37.5714, lng: 126.9658 },
  { stationId: '119', stationName: '수원', region: '경기도',     lat: 37.2636, lng: 127.0286 },
  { stationId: '133', stationName: '대전', region: '대전광역시', lat: 36.3703, lng: 127.3847 },
  { stationId: '143', stationName: '대구', region: '대구광역시', lat: 35.8733, lng: 128.5966 },
  { stationId: '156', stationName: '광주', region: '광주광역시', lat: 35.1569, lng: 126.8526 },
  { stationId: '159', stationName: '부산', region: '부산광역시', lat: 35.1044, lng: 129.0320 },
]

export const MOCK_ROAD_DAMAGE = [
  { id: 1,  damageType: 'pothole', confidence: 0.94, latitude: 37.5083, longitude: 127.0232, roadName: '테헤란로',   district: '강남구',   detectedAt: '2025-12-15T09:30:00' },
  { id: 2,  damageType: 'pothole', confidence: 0.87, latitude: 37.5044, longitude: 127.0024, roadName: '반포대로',   district: '서초구',   detectedAt: '2025-12-20T14:22:00' },
  { id: 3,  damageType: 'pothole', confidence: 0.91, latitude: 37.5563, longitude: 126.9238, roadName: '와우산로',   district: '마포구',   detectedAt: '2025-12-22T10:05:00' },
  { id: 4,  damageType: 'pothole', confidence: 0.78, latitude: 37.5088, longitude: 127.1153, roadName: '올림픽로',   district: '송파구',   detectedAt: '2025-12-25T08:15:00' },
  { id: 5,  damageType: 'pothole', confidence: 0.85, latitude: 37.5344, longitude: 126.9942, roadName: '이태원로',   district: '용산구',   detectedAt: '2025-12-28T16:40:00' },
  { id: 6,  damageType: 'pothole', confidence: 0.92, latitude: 37.6550, longitude: 127.0620, roadName: '동일로',     district: '노원구',   detectedAt: '2026-01-02T09:20:00' },
  { id: 7,  damageType: 'pothole', confidence: 0.76, latitude: 37.5384, longitude: 127.1238, roadName: '천호대로',   district: '강동구',   detectedAt: '2026-01-05T11:33:00' },
  { id: 8,  damageType: 'pothole', confidence: 0.89, latitude: 37.4848, longitude: 126.9520, roadName: '봉천로',     district: '관악구',   detectedAt: '2026-01-07T14:50:00' },
  { id: 9,  damageType: 'pothole', confidence: 0.83, latitude: 37.6166, longitude: 126.9220, roadName: '통일로',     district: '은평구',   detectedAt: '2026-01-10T07:45:00' },
  { id: 10, damageType: 'pothole', confidence: 0.96, latitude: 37.5641, longitude: 126.9990, roadName: '을지로',     district: '중구',     detectedAt: '2026-01-12T13:25:00' },
  { id: 11, damageType: 'crack',   confidence: 0.88, latitude: 37.6688, longitude: 127.0470, roadName: '도봉로',     district: '도봉구',   detectedAt: '2025-12-10T08:30:00' },
  { id: 12, damageType: 'crack',   confidence: 0.72, latitude: 37.6379, longitude: 127.0255, roadName: '미아로',     district: '강북구',   detectedAt: '2025-12-12T10:15:00' },
  { id: 13, damageType: 'crack',   confidence: 0.81, latitude: 37.6059, longitude: 127.0929, roadName: '망우로',     district: '중랑구',   detectedAt: '2025-12-14T09:00:00' },
  { id: 14, damageType: 'crack',   confidence: 0.69, latitude: 37.5540, longitude: 127.0748, roadName: '뚝섬로',     district: '광진구',   detectedAt: '2025-12-16T11:45:00' },
  { id: 15, damageType: 'crack',   confidence: 0.93, latitude: 37.5636, longitude: 127.0369, roadName: '왕십리로',   district: '성동구',   detectedAt: '2025-12-18T15:20:00' },
  { id: 16, damageType: 'crack',   confidence: 0.77, latitude: 37.5870, longitude: 127.0562, roadName: '돌곶이로',   district: '성북구',   detectedAt: '2025-12-21T13:10:00' },
  { id: 17, damageType: 'crack',   confidence: 0.84, latitude: 37.5742, longitude: 127.0405, roadName: '전농로',     district: '동대문구', detectedAt: '2025-12-23T08:55:00' },
  { id: 18, damageType: 'crack',   confidence: 0.71, latitude: 37.4895, longitude: 126.9396, roadName: '보라매로',   district: '동작구',   detectedAt: '2025-12-26T10:30:00' },
  { id: 19, damageType: 'crack',   confidence: 0.86, latitude: 37.4565, longitude: 126.8951, roadName: '시흥대로',   district: '금천구',   detectedAt: '2025-12-29T14:00:00' },
  { id: 20, damageType: 'crack',   confidence: 0.79, latitude: 37.4853, longitude: 126.8995, roadName: '가마산로',   district: '구로구',   detectedAt: '2026-01-03T09:45:00' },
  { id: 21, damageType: 'crack',   confidence: 0.90, latitude: 37.5167, longitude: 126.8540, roadName: '오목로',     district: '양천구',   detectedAt: '2026-01-04T12:30:00' },
  { id: 22, damageType: 'crack',   confidence: 0.75, latitude: 37.5177, longitude: 126.9007, roadName: '당산로',     district: '영등포구', detectedAt: '2026-01-06T11:00:00' },
  { id: 23, damageType: 'crack',   confidence: 0.88, latitude: 37.5508, longitude: 126.8496, roadName: '공항대로',   district: '강서구',   detectedAt: '2026-01-08T09:15:00' },
  { id: 24, damageType: 'crack',   confidence: 0.82, latitude: 37.5562, longitude: 126.9388, roadName: '신촌로',     district: '서대문구', detectedAt: '2026-01-09T14:40:00' },
  { id: 25, damageType: 'crack',   confidence: 0.74, latitude: 37.5726, longitude: 126.9791, roadName: '종로',       district: '종로구',   detectedAt: '2026-01-10T10:20:00' },
  { id: 26, damageType: 'crack',   confidence: 0.91, latitude: 37.5153, longitude: 127.0590, roadName: '삼성로',     district: '강남구',   detectedAt: '2026-01-11T08:00:00' },
  { id: 27, damageType: 'crack',   confidence: 0.67, latitude: 37.4979, longitude: 127.0276, roadName: '강남대로',   district: '서초구',   detectedAt: '2026-01-11T16:30:00' },
  { id: 28, damageType: 'crack',   confidence: 0.85, latitude: 37.4770, longitude: 127.1400, roadName: '위례성대로', district: '송파구',   detectedAt: '2026-01-12T09:50:00' },
  { id: 29, damageType: 'crack',   confidence: 0.78, latitude: 37.5500, longitude: 127.0196, roadName: '독서당로',   district: '성동구',   detectedAt: '2026-01-13T11:35:00' },
  { id: 30, damageType: 'crack',   confidence: 0.83, latitude: 37.6350, longitude: 127.0713, roadName: '노해로',     district: '노원구',   detectedAt: '2026-01-14T07:55:00' },
]

export const MOCK_BLACKICE = [
  { id: 1,  stationId: '108', riskLevel: 3, riskLabel: '위험', temperature: -5.2, humidity: 85, precipitation: 1.2, windSpeed: 4.5, predictedAt: '2026-01-15T06:00:00' },
  { id: 2,  stationId: '108', riskLevel: 2, riskLabel: '주의', temperature: -3.1, humidity: 78, precipitation: 0.5, windSpeed: 3.2, predictedAt: '2026-01-14T18:00:00' },
  { id: 3,  stationId: '108', riskLevel: 2, riskLabel: '주의', temperature: -2.8, humidity: 72, precipitation: 0.0, windSpeed: 2.8, predictedAt: '2026-01-14T06:00:00' },
  { id: 4,  stationId: '119', riskLevel: 3, riskLabel: '위험', temperature: -6.5, humidity: 90, precipitation: 2.1, windSpeed: 5.3, predictedAt: '2026-01-15T06:00:00' },
  { id: 5,  stationId: '119', riskLevel: 2, riskLabel: '주의', temperature: -4.2, humidity: 82, precipitation: 1.0, windSpeed: 4.0, predictedAt: '2026-01-14T18:00:00' },
  { id: 6,  stationId: '119', riskLevel: 1, riskLabel: '관심', temperature: -1.5, humidity: 68, precipitation: 0.0, windSpeed: 2.1, predictedAt: '2026-01-14T06:00:00' },
  { id: 7,  stationId: '133', riskLevel: 1, riskLabel: '관심', temperature: -1.8, humidity: 65, precipitation: 0.0, windSpeed: 2.5, predictedAt: '2026-01-15T06:00:00' },
  { id: 8,  stationId: '133', riskLevel: 0, riskLabel: '안전', temperature:  2.3, humidity: 55, precipitation: 0.0, windSpeed: 1.8, predictedAt: '2026-01-14T18:00:00' },
  { id: 9,  stationId: '133', riskLevel: 0, riskLabel: '안전', temperature:  3.5, humidity: 50, precipitation: 0.0, windSpeed: 1.5, predictedAt: '2026-01-14T06:00:00' },
  { id: 10, stationId: '143', riskLevel: 1, riskLabel: '관심', temperature: -0.5, humidity: 60, precipitation: 0.0, windSpeed: 2.0, predictedAt: '2026-01-15T06:00:00' },
  { id: 11, stationId: '143', riskLevel: 0, riskLabel: '안전', temperature:  1.2, humidity: 52, precipitation: 0.0, windSpeed: 1.6, predictedAt: '2026-01-14T18:00:00' },
  { id: 12, stationId: '143', riskLevel: 0, riskLabel: '안전', temperature:  2.8, humidity: 48, precipitation: 0.0, windSpeed: 1.3, predictedAt: '2026-01-14T06:00:00' },
  { id: 13, stationId: '156', riskLevel: 2, riskLabel: '주의', temperature: -2.5, humidity: 76, precipitation: 0.8, windSpeed: 3.5, predictedAt: '2026-01-15T06:00:00' },
  { id: 14, stationId: '156', riskLevel: 1, riskLabel: '관심', temperature: -0.8, humidity: 70, precipitation: 0.2, windSpeed: 2.8, predictedAt: '2026-01-14T18:00:00' },
  { id: 15, stationId: '156', riskLevel: 0, riskLabel: '안전', temperature:  1.5, humidity: 62, precipitation: 0.0, windSpeed: 2.0, predictedAt: '2026-01-14T06:00:00' },
  { id: 16, stationId: '159', riskLevel: 0, riskLabel: '안전', temperature:  3.5, humidity: 58, precipitation: 0.0, windSpeed: 3.2, predictedAt: '2026-01-15T06:00:00' },
  { id: 17, stationId: '159', riskLevel: 0, riskLabel: '안전', temperature:  4.2, humidity: 55, precipitation: 0.0, windSpeed: 2.8, predictedAt: '2026-01-14T18:00:00' },
  { id: 18, stationId: '159', riskLevel: 1, riskLabel: '관심', temperature:  1.8, humidity: 72, precipitation: 0.3, windSpeed: 4.5, predictedAt: '2026-01-14T06:00:00' },
]

export const MOCK_CURRENT_WEATHER = [
  { stationId: '108', riskLevel: 3, riskLabel: '위험', temperature: -5.2, humidity: 85, precipitation: 1.2, windSpeed: 4.5, predictedAt: '2026-01-15T06:00:00' },
  { stationId: '119', riskLevel: 3, riskLabel: '위험', temperature: -6.5, humidity: 90, precipitation: 2.1, windSpeed: 5.3, predictedAt: '2026-01-15T06:00:00' },
  { stationId: '133', riskLevel: 1, riskLabel: '관심', temperature: -1.8, humidity: 65, precipitation: 0.0, windSpeed: 2.5, predictedAt: '2026-01-15T06:00:00' },
  { stationId: '143', riskLevel: 1, riskLabel: '관심', temperature: -0.5, humidity: 60, precipitation: 0.0, windSpeed: 2.0, predictedAt: '2026-01-15T06:00:00' },
  { stationId: '156', riskLevel: 2, riskLabel: '주의', temperature: -2.5, humidity: 76, precipitation: 0.8, windSpeed: 3.5, predictedAt: '2026-01-15T06:00:00' },
  { stationId: '159', riskLevel: 0, riskLabel: '안전', temperature:  3.5, humidity: 58, precipitation: 0.0, windSpeed: 3.2, predictedAt: '2026-01-15T06:00:00' },
]

export const MOCK_ROAD_STATS = {
  totalCount: 247,
  potholeCount: 89,
  crackCount: 158,
  byType: [
    { type: 'pothole', count: 89 },
    { type: 'crack',   count: 158 },
  ],
}

export const MOCK_BLACKICE_STATS = {
  totalCount: 72,
  byRiskLevel: [
    { level: 0, count: 28 },
    { level: 1, count: 24 },
    { level: 2, count: 13 },
    { level: 3, count: 7  },
  ],
}

export const MOCK_DISTRICTS = [
  '강남구', '강동구', '강북구', '강서구', '관악구',
  '광진구', '구로구', '금천구', '노원구', '도봉구',
  '동대문구', '동작구', '마포구', '서대문구', '서초구',
  '성동구', '성북구', '송파구', '양천구', '영등포구',
  '용산구', '은평구', '종로구', '중구', '중랑구',
]

const ok = (data) => Promise.resolve({ data: { code: 'SUCCESS', data } })

export const mockRoadDamageApi = {
  getList: (params) => {
    const page = params?.page || 0
    const size = params?.size || 20
    let items = [...MOCK_ROAD_DAMAGE]
    if (params?.damageType) items = items.filter(i => i.damageType === params.damageType)
    if (params?.district)   items = items.filter(i => i.district.includes(params.district))
    const content = items.slice(page * size, (page + 1) * size)
    return ok({ content, totalElements: items.length, totalPages: Math.ceil(items.length / size), number: page })
  },
  getOne: (id) => ok(MOCK_ROAD_DAMAGE.find(d => d.id === Number(id))),
  getMapData: (bbox) => {
    const features = MOCK_ROAD_DAMAGE
      .filter(d => d.longitude >= bbox[0] && d.latitude >= bbox[1] && d.longitude <= bbox[2] && d.latitude <= bbox[3])
      .map(d => ({
        id: d.id,
        geometry: { type: 'Point', coordinates: [d.longitude, d.latitude] },
        properties: { damageType: d.damageType, confidence: d.confidence, roadName: d.roadName, district: d.district, detectedAt: d.detectedAt },
      }))
    return ok(features)
  },
  getStats:    () => ok(MOCK_ROAD_STATS),
  getDistricts: () => ok(MOCK_DISTRICTS),
}

export const mockBlackIceApi = {
  getList: (params) => {
    const page = params?.page || 0
    const size = params?.size || 20
    let items = [...MOCK_BLACKICE]
    if (params?.riskLevel !== undefined && params.riskLevel !== '') {
      items = items.filter(i => i.riskLevel === Number(params.riskLevel))
    }
    const content = items.slice(page * size, (page + 1) * size)
    return ok({ content, totalElements: items.length, totalPages: Math.ceil(items.length / size), number: page })
  },
  getMapData: (bbox) => {
    const features = MOCK_STATIONS
      .filter(s => s.lng >= bbox[0] && s.lat >= bbox[1] && s.lng <= bbox[2] && s.lat <= bbox[3])
      .map(s => {
        const w = MOCK_CURRENT_WEATHER.find(w => w.stationId === s.stationId) || MOCK_CURRENT_WEATHER[0]
        return {
          id: s.stationId,
          geometry: { type: 'Point', coordinates: [s.lng, s.lat] },
          properties: { ...w, stationId: s.stationId },
        }
      })
    return ok(features)
  },
  getStats:        () => ok(MOCK_BLACKICE_STATS),
  getStations:     () => ok(MOCK_STATIONS),
  getCurrentWeather: () => ok(MOCK_CURRENT_WEATHER),
  getRegionWeather: (lat, lng) => {
    const station = MOCK_STATIONS.reduce((a, b) =>
      Math.hypot(a.lat - lat, a.lng - lng) < Math.hypot(b.lat - lat, b.lng - lng) ? a : b
    )
    const w = MOCK_CURRENT_WEATHER.find(w => w.stationId === station.stationId) || MOCK_CURRENT_WEATHER[0]
    return ok(w)
  },
}
