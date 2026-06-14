<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<!--
  QGIS 스타일 파일 — 도로 파손 레이어용
  QGIS에서 레이어 → 속성 → 스타일 → 스타일 불러오기로 적용
-->
<qgis version="3.28" styleCategories="AllStyleCategories">
  <renderer-v2 type="categorizedSymbol" attr="damage_type" forceraster="0">
    <categories>
      <category value="pothole" label="포트홀" render="true">
        <symbol type="marker" name="pothole">
          <layer class="SimpleMarker">
            <prop k="color" v="198,40,40,255"/>
            <prop k="size" v="4"/>
            <prop k="outline_style" v="solid"/>
            <prop k="outline_color" v="255,255,255,255"/>
            <prop k="outline_width" v="0.5"/>
          </layer>
        </symbol>
      </category>
      <category value="crack" label="균열" render="true">
        <symbol type="marker" name="crack">
          <layer class="SimpleMarker">
            <prop k="color" v="230,81,0,255"/>
            <prop k="size" v="3"/>
            <prop k="name" v="triangle"/>
            <prop k="outline_style" v="solid"/>
            <prop k="outline_color" v="255,255,255,255"/>
            <prop k="outline_width" v="0.5"/>
          </layer>
        </symbol>
      </category>
    </categories>
  </renderer-v2>
</qgis>
