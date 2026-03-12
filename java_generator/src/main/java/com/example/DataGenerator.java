package com.example;

import com.opencsv.CSVWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Random;

/**
 * Generates synthetic sales data for the data engineering pipeline.
 * Creates CSV files with realistic e-commerce sales data.
 */
public class DataGenerator {

    private static final String[] CATEGORIES = {
        "Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Beauty", "Toys", "Automotive"
    };

    private static final String[] PRODUCTS = {
        "Laptop", "Smartphone", "Headphones", "T-Shirt", "Jeans", "Coffee Maker", "Basketball",
        "Novel", "Shampoo", "Action Figure", "Car Battery", "Tablet", "Dress", "Garden Hose",
        "Running Shoes", "Cookbook", "Makeup Kit", "Drone", "Engine Oil"
    };

    private final Random random = new Random();
    private final DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    public void generateSalesData(String outputPath, int numRecords) throws IOException {
        try (CSVWriter writer = new CSVWriter(new FileWriter(outputPath))) {
            // Write header
            writer.writeNext(new String[]{
                "date", "product_id", "product_name", "category", "quantity", "unit_price", "total_amount"
            });

            // Generate records
            LocalDate today = LocalDate.now();
            for (int i = 0; i < numRecords; i++) {
                String date = today.minusDays(random.nextInt(30)).format(dateFormatter);
                String productId = String.format("P%04d", random.nextInt(1000) + 1);
                String productName = PRODUCTS[random.nextInt(PRODUCTS.length)];
                String category = CATEGORIES[random.nextInt(CATEGORIES.length)];
                int quantity = random.nextInt(10) + 1;
                double unitPrice = Math.round((random.nextDouble() * 500 + 10) * 100.0) / 100.0;
                double totalAmount = Math.round(quantity * unitPrice * 100.0) / 100.0;

                writer.writeNext(new String[]{
                    date,
                    productId,
                    productName,
                    category,
                    String.valueOf(quantity),
                    String.valueOf(unitPrice),
                    String.valueOf(totalAmount)
                });
            }
        }
    }

    public static void main(String[] args) {
        if (args.length != 2) {
            System.err.println("Usage: java -jar data-generator.jar <output_path> <num_records>");
            System.exit(1);
        }

        String outputPath = args[0];
        int numRecords = Integer.parseInt(args[1]);

        DataGenerator generator = new DataGenerator();
        try {
            generator.generateSalesData(outputPath, numRecords);
            System.out.println("Generated " + numRecords + " sales records to " + outputPath);
        } catch (IOException e) {
            System.err.println("Error generating data: " + e.getMessage());
            System.exit(1);
        }
    }
}