import { create } from 'zustand'

export const useMapStore = create((set) => ({
  showDamage: true,
  showBlackIce: true,
  selectedDamageType: null,   // null | 'pothole' | 'crack'
  selectedRiskLevel: null,    // null | 0 | 1 | 2 | 3
  bbox: [124.0, 33.0, 132.0, 39.0],  // [minLng, minLat, maxLng, maxLat]
  // { stationId, stationName, region, lat, lng } | null
  selectedRegion: null,
  selectedDistrict: null,     // road_damage.district 값
  setShowDamage: (v) => set({ showDamage: v }),
  setShowBlackIce: (v) => set({ showBlackIce: v }),
  setSelectedDamageType: (v) => set({ selectedDamageType: v }),
  setSelectedRiskLevel: (v) => set({ selectedRiskLevel: v }),
  setBbox: (bbox) => set({ bbox }),
  setSelectedRegion: (region) => set({ selectedRegion: region }),
  setSelectedDistrict: (district) => set({ selectedDistrict: district }),
}))
