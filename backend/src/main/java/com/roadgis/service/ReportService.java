package com.roadgis.service;

import com.itextpdf.kernel.pdf.*;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.element.Paragraph;
import com.itextpdf.layout.element.Table;
import com.roadgis.entity.BlackIceRisk;
import com.roadgis.entity.RoadDamage;
import com.roadgis.repository.BlackIceRiskRepository;
import com.roadgis.repository.RoadDamageRepository;
import lombok.RequiredArgsConstructor;
import org.apache.poi.ss.usermodel.CellStyle;
import org.apache.poi.ss.usermodel.Font;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ReportService {

    private final RoadDamageRepository roadDamageRepository;
    private final BlackIceRiskRepository blackIceRiskRepository;

    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

    public byte[] generateExcel() {
        try (XSSFWorkbook workbook = new XSSFWorkbook();
             ByteArrayOutputStream out = new ByteArrayOutputStream()) {

            // 도로 파손 시트
            Sheet damageSheet = workbook.createSheet("도로파손");
            String[] damageHeaders = {"ID", "유형", "신뢰도", "위도", "경도", "도로명", "행정구역", "탐지일시"};
            createHeaderRow(workbook, damageSheet, damageHeaders);

            List<RoadDamage> damages = roadDamageRepository.findAll(PageRequest.of(0, 1000)).getContent();
            int rowIdx = 1;
            for (RoadDamage d : damages) {
                Row row = damageSheet.createRow(rowIdx++);
                row.createCell(0).setCellValue(d.getId());
                row.createCell(1).setCellValue(d.getDamageType());
                row.createCell(2).setCellValue(String.format("%.2f", d.getConfidence()));
                row.createCell(3).setCellValue(d.getLocation().getY());
                row.createCell(4).setCellValue(d.getLocation().getX());
                row.createCell(5).setCellValue(d.getRoadName() != null ? d.getRoadName() : "");
                row.createCell(6).setCellValue(d.getDistrict() != null ? d.getDistrict() : "");
                row.createCell(7).setCellValue(d.getDetectedAt().format(FMT));
            }

            // 블랙아이스 시트
            Sheet iceSheet = workbook.createSheet("블랙아이스");
            String[] iceHeaders = {"ID", "관측소", "위험레벨", "위험등급", "기온", "습도", "강수량", "풍속", "예측일시"};
            createHeaderRow(workbook, iceSheet, iceHeaders);

            List<BlackIceRisk> risks = blackIceRiskRepository.findAll(PageRequest.of(0, 1000)).getContent();
            rowIdx = 1;
            for (BlackIceRisk r : risks) {
                Row row = iceSheet.createRow(rowIdx++);
                row.createCell(0).setCellValue(r.getId());
                row.createCell(1).setCellValue(r.getStationId());
                row.createCell(2).setCellValue(r.getRiskLevel());
                row.createCell(3).setCellValue(r.getRiskLabel());
                row.createCell(4).setCellValue(r.getTemperature() != null ? r.getTemperature() : 0);
                row.createCell(5).setCellValue(r.getHumidity() != null ? r.getHumidity() : 0);
                row.createCell(6).setCellValue(r.getPrecipitation() != null ? r.getPrecipitation() : 0);
                row.createCell(7).setCellValue(r.getWindSpeed() != null ? r.getWindSpeed() : 0);
                row.createCell(8).setCellValue(r.getPredictedAt().format(FMT));
            }

            workbook.write(out);
            return out.toByteArray();
        } catch (IOException e) {
            throw new IllegalStateException("Excel 보고서 생성 실패", e);
        }
    }

    public byte[] generatePdf() {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        PdfWriter writer = new PdfWriter(out);
        PdfDocument pdf = new PdfDocument(writer);
        Document document = new Document(pdf);

        document.add(new Paragraph("도로 안전 관리 보고서").setBold().setFontSize(18));
        document.add(new Paragraph(" "));

        // 도로 파손 요약
        document.add(new Paragraph("1. 도로 파손 현황").setBold().setFontSize(14));
        long totalDamage = roadDamageRepository.count();
        long potholes = roadDamageRepository.countByDamageType("pothole");
        long cracks = roadDamageRepository.countByDamageType("crack");
        document.add(new Paragraph(String.format("  - 전체: %d건 (포트홀: %d건, 균열: %d건)", totalDamage, potholes, cracks)));

        document.add(new Paragraph(" "));
        document.add(new Paragraph("2. 블랙아이스 위험도 현황").setBold().setFontSize(14));
        long totalRisk = blackIceRiskRepository.count();
        document.add(new Paragraph(String.format("  - 전체 예측 건수: %d건", totalRisk)));

        // 테이블 (최근 10건)
        document.add(new Paragraph(" "));
        document.add(new Paragraph("3. 최근 도로 파손 탐지 목록").setBold().setFontSize(14));
        Table table = new Table(5);
        table.addHeaderCell(new com.itextpdf.layout.element.Cell().add(new Paragraph("ID")));
        table.addHeaderCell(new com.itextpdf.layout.element.Cell().add(new Paragraph("유형")));
        table.addHeaderCell(new com.itextpdf.layout.element.Cell().add(new Paragraph("신뢰도")));
        table.addHeaderCell(new com.itextpdf.layout.element.Cell().add(new Paragraph("행정구역")));
        table.addHeaderCell(new com.itextpdf.layout.element.Cell().add(new Paragraph("탐지일시")));

        List<RoadDamage> recent = roadDamageRepository.findAll(PageRequest.of(0, 10)).getContent();
        for (RoadDamage d : recent) {
            table.addCell(String.valueOf(d.getId()));
            table.addCell(d.getDamageType());
            table.addCell(String.format("%.2f", d.getConfidence()));
            table.addCell(d.getDistrict() != null ? d.getDistrict() : "-");
            table.addCell(d.getDetectedAt().format(FMT));
        }
        document.add(table);

        document.close();
        return out.toByteArray();
    }

    private void createHeaderRow(XSSFWorkbook workbook, Sheet sheet, String[] headers) {
        CellStyle style = workbook.createCellStyle();
        Font font = workbook.createFont();
        font.setBold(true);
        style.setFont(font);

        Row header = sheet.createRow(0);
        for (int i = 0; i < headers.length; i++) {
            org.apache.poi.ss.usermodel.Cell cell = header.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(style);
        }
    }
}
