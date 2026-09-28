from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    page.goto('http://localhost:3000/dashboard/chat')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    inp = page.locator('input[placeholder*="Ask anything"]').first
    inp.fill('Can you compare B-Trees with Log-Structured Merge trees?')
    page.keyboard.press('Enter')
    time.sleep(3.5)

    # Now type follow-up
    inp.fill('summarize it')
    page.keyboard.press('Enter')
    time.sleep(3.5)

    page.screenshot(path='reports_assets/2_chat_playground.png')
    print('reports_assets/2_chat_playground.png captured with full conversation!')
    browser.close()
