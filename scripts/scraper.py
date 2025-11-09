"""
SHL Product Catalog Scraper - Final Version
Scrapes all 32 pages of the SHL product catalog and saves to Excel.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import time

# Mapping for star rating data-value to Yes/No
RATING_MAP = {
    "0": "No",
    "1": "Yes",
    "2": "Yes",
    "3": "Yes",
    "4": "Yes",
    "5": "Yes"
}

def setup_driver():
    """
    Set up Selenium Chrome driver in headed mode.
    
    Returns:
        WebDriver instance and WebDriverWait instance
    """
    print("Setting up Chrome driver...")
    
    # Configure Chrome options for headed mode
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Initialize Chrome driver with automatic driver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Create wait object with 15 second timeout
    wait = WebDriverWait(driver, 15)
    
    print("✓ Chrome driver initialized successfully\n")
    return driver, wait

def handle_cookie_consent(driver, wait):
    """
    Handle the cookie consent popup on the main page.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    """
    try:
        print("Handling cookie consent popup...")
        allow_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Allow all cookies')]"))
        )
        driver.execute_script("arguments[0].click();", allow_button)
        print("✓ Cookie consent handled\n")
        time.sleep(3)
    except Exception as e:
        print(f"! Cookie popup not found or already handled: {e}\n")

def scrape_all_product_urls(driver, wait):
    """
    Scrape all product URLs from all 32 pages of the catalog.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    
    Returns:
        List of all unique product URLs
    """
    print("=" * 70)
    print("STEP 1: Collecting All Product URLs from All Pages")
    print("=" * 70 + "\n")
    
    all_product_urls = []
    page_number = 1
    
    # Container XPATH
    container_xpath = "/html/body/main/div[3]/div/div/div/div[3]/div"
    
    while True:
        print(f"Scraping page {page_number}...")
        
        try:
            # Wait for container to be present
            container = wait.until(EC.presence_of_element_located((By.XPATH, container_xpath)))
            
            # Find all links within the container
            links = container.find_elements(By.TAG_NAME, "a")
            
            # Extract URLs containing '/view/'
            page_urls = []
            for link in links:
                href = link.get_attribute('href')
                if href and '/view/' in href and href not in all_product_urls:
                    all_product_urls.append(href)
                    page_urls.append(href)
            
            print(f"  ✓ Found {len(page_urls)} products on page {page_number}")
            
        except TimeoutException:
            print(f"  ✗ Timeout waiting for container on page {page_number}")
            break
        
        # Try to find and click the Next button
        try:
            next_button = driver.find_element(By.CLASS_NAME, "c-pager__next")
            
            # Check if Next button is disabled
            if next_button.get_attribute("aria-disabled") == "true":
                print(f"\n✓ Reached last page (page {page_number})")
                break
            
            # Click the Next button using JavaScript
            driver.execute_script("arguments[0].click();", next_button)
            print(f"  → Moving to page {page_number + 1}...")
            
            page_number += 1
            time.sleep(2)  # Wait for next page to load
            
        except NoSuchElementException:
            print(f"\n✓ No more pages found (completed {page_number} pages)")
            break
    
    print(f"\n✓ Total unique product URLs collected: {len(all_product_urls)}\n")
    return all_product_urls

def scrape_product_page(driver, wait, url):
    """
    Scrape data from a single product page.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        url: Product page URL
    
    Returns:
        Dictionary containing product information
    """
    driver.get(url)
    
    # Initialize product info dictionary
    product_info = {'url': url}
    
    # Scrape Name
    try:
        name = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "c-hero-v1__title"))).text
        product_info['name'] = name
    except (NoSuchElementException, TimeoutException):
        product_info['name'] = None
    
    # Scrape Description
    try:
        desc = driver.find_element(By.CLASS_NAME, "c-hero-v1__description").text
        product_info['description'] = desc
    except NoSuchElementException:
        product_info['description'] = None
    
    # Scrape Test Types (NEW LOGIC)
    try:
        test_type_elements = driver.find_elements(By.CLASS_NAME, "c-pill-list__item")
        test_types = [
            el.find_element(By.TAG_NAME, "span").get_attribute("data-text") 
            for el in test_type_elements
        ]
        product_info['test_type'] = str(test_types)  # Save as string representation of list
    except:
        product_info['test_type'] = "[]"
    
    # Initialize key features fields
    product_info['duration'] = None
    product_info['adaptive_support'] = None
    product_info['remote_support'] = None
    
    # Scrape Key Features (NEW LOGIC for Dots/Text)
    try:
        key_features = driver.find_elements(By.CLASS_NAME, "c-key-features__item")
        
        for item in key_features:
            try:
                label = item.find_element(By.CLASS_NAME, "c-key-features__item-label").text.strip()
                
                # Check if this is a rating (dots) field
                try:
                    data_val = item.find_element(By.CLASS_NAME, "c-star-rating").get_attribute("data-value")
                    value = RATING_MAP.get(data_val, "No")
                except NoSuchElementException:
                    # Not a rating field, get text value
                    value = item.find_element(By.CLASS_NAME, "c-key-features__item-value").text.strip()
                
                # Map to appropriate field
                if label == "Duration":
                    try:
                        # Extract number from "X min" format
                        product_info['duration'] = int(value.replace(" min", "").strip())
                    except (ValueError, AttributeError):
                        product_info['duration'] = None
                elif label == "Adaptive Support":
                    product_info['adaptive_support'] = value
                elif label == "Remote Support":
                    product_info['remote_support'] = value
                    
            except NoSuchElementException:
                continue
                
    except NoSuchElementException:
        pass
    
    return product_info

def scrape_all_products(driver, wait, product_urls):
    """
    Scrape data from all product pages.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        product_urls: List of product URLs to scrape
    
    Returns:
        List of dictionaries containing product data
    """
    print("=" * 70)
    print("STEP 2: Scraping Individual Product Pages")
    print("=" * 70 + "\n")
    
    scraped_data = []
    
    for i, url in enumerate(product_urls, 1):
        print(f"[{i}/{len(product_urls)}] Scraping: {url}")
        
        try:
            product_info = scrape_product_page(driver, wait, url)
            scraped_data.append(product_info)
            print(f"  ✓ Scraped: {product_info.get('name', 'Unknown')}\n")
        except Exception as e:
            print(f"  ✗ Error scraping product: {e}\n")
            # Add URL with empty data to maintain record
            scraped_data.append({
                'url': url,
                'name': None,
                'description': None,
                'test_type': "[]",
                'duration': None,
                'adaptive_support': None,
                'remote_support': None
            })
        
        # Be polite to the server
        time.sleep(1)
    
    print(f"✓ Completed scraping {len(scraped_data)} products\n")
    return scraped_data

def save_to_excel(scraped_data, output_path='data/crawled_data.xlsx'):
    """
    Save scraped data to Excel file.
    
    Args:
        scraped_data: List of dictionaries containing product data
        output_path: Path to output Excel file
    """
    print("=" * 70)
    print("STEP 3: Saving Data to Excel")
    print("=" * 70 + "\n")
    
    # Convert to DataFrame
    df = pd.DataFrame(scraped_data)
    
    # Ensure columns are in the correct order
    column_order = ['name', 'url', 'description', 'adaptive_support', 
                   'duration', 'remote_support', 'test_type']
    
    # Reorder columns (add any missing columns with None values)
    for col in column_order:
        if col not in df.columns:
            df[col] = None
    
    df = df[column_order]
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save to Excel
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    print(f"✓ Scraping complete! Saved {len(scraped_data)} products to {output_path}")
    
    # Display summary statistics
    print(f"\n{'=' * 70}")
    print("Summary Statistics")
    print("=" * 70)
    print(f"Total products: {len(df)}")
    print(f"Products with names: {df['name'].notna().sum()}")
    print(f"Products with descriptions: {df['description'].notna().sum()}")
    print(f"Products with duration: {df['duration'].notna().sum()}")
    print(f"Products with adaptive support: {df['adaptive_support'].notna().sum()}")
    print(f"Products with remote support: {df['remote_support'].notna().sum()}")
    print(f"Products with test types: {df['test_type'].apply(lambda x: x != '[]').sum()}")
    print("=" * 70)

def main():
    """
    Main execution function.
    """
    print("=" * 70)
    print("SHL Product Catalog Scraper - Final Version")
    print("=" * 70 + "\n")
    
    driver = None
    
    try:
        # Setup driver
        driver, wait = setup_driver()
        
        # Navigate to main catalog page
        catalog_url = "https://www.shl.com/solutions/products/product-catalog/"
        print(f"Navigating to: {catalog_url}")
        driver.get(catalog_url)
        print("✓ Page loaded\n")
        
        # Handle cookie consent
        handle_cookie_consent(driver, wait)
        
        # Scrape all product URLs from all pages
        all_product_urls = scrape_all_product_urls(driver, wait)
        
        if not all_product_urls:
            print("✗ No product URLs found. Exiting.")
            return
        
        # Scrape each product page
        scraped_data = scrape_all_products(driver, wait, all_product_urls)
        
        # Save to Excel
        save_to_excel(scraped_data)
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Always close the browser
        if driver:
            print("\nClosing browser...")
            driver.quit()
            print("✓ Browser closed successfully")
    
    print("\n" + "=" * 70)
    print("Script execution complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()