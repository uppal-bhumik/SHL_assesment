"""
SHL Product Page Debug Script
This script opens a single product page in visible Chrome browser
and pauses for 5 minutes to allow manual inspection of elements.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

def main():
    """
    Main debug function - opens a product page and pauses for inspection.
    """
    print("=" * 70)
    print("SHL Product Page Debug Script")
    print("=" * 70 + "\n")
    
    # Setup Chrome options for HEADED mode (visible browser)
    print("Setting up Chrome driver in VISIBLE mode...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    # Initialize Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    print("✓ Chrome driver initialized\n")
    
    try:
        # Navigate to a single product page
        test_url = "https://www.shl.com/products/product-catalog/view/net-framework-4-5/"
        print(f"Navigating to: {test_url}")
        driver.get(test_url)
        
        print("✓ Page loaded\n")
        
        # Wait a moment for page to fully render
        time.sleep(3)
        
        # DEBUG PAUSE
        print("\n" + "=" * 70)
        print("!!! SCRIPT PAUSED FOR 300 SECONDS FOR CONTENT RECON !!!")
        print("=" * 70)
        print("!!! 1. GO TO THE CHROME WINDOW THE SCRIPT OPENED.")
        print("!!! 2. PRESS F12 TO OPEN DEVTOOLS.")
        print("!!! 3. Use the Inspector tool to find the following items and report their CLASS or ID:")
        print("!!!    - The 'Test Type' letters (like 'K' or 'P')")
        print("!!!    - The 'Dots' for 'Adaptive Support' (find the data-value attribute)")
        print("!!! 4. Go back to the MAIN catalog page (or open it in a new tab) and find:")
        print("!!!    - The 'Next Page' button (the '>' arrow)")
        print("=" * 70 + "\n")
        
        print("⏰ Pausing for 300 seconds (5 minutes)...\n")
        print("💡 TIP: You can close the browser window when done to end the script early.\n")
        
        # Pause for 300 seconds (5 minutes)
        time.sleep(300)
        
        print("\n✓ Debug pause complete.")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Close the browser
        print("\nClosing browser...")
        driver.quit()
        print("✓ Browser closed successfully")
    
    print("\n" + "=" * 70)
    print("Debug script complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()