"""
Focused Playwright test script for the SKILLBRIDGE P0 application flow regression.
This is the same flow executed through the browser automation tool during iteration 3 verification.
"""

async def run(page):
    await page.set_viewport_size({"width": 1920, "height": 1080})
    await page.goto("http://localhost:3000/")
    await page.evaluate("localStorage.clear()")
    await page.goto("http://localhost:3000/student/login")
    await page.locator('[data-testid="demo-access-button"]').click()
    await page.wait_for_url("**/home", timeout=10000)
    await page.locator('[data-testid="nav-opportunities-link"]').click()
    await page.locator('[data-testid="view-opportunity-frontend-intern"]').click()
    await page.locator('[data-testid="apply-now-button"]').click()
    await page.locator('[data-testid="application-step-1"]').wait_for(timeout=10000)
    await page.locator('[data-testid="application-next-button"]').click()
    await page.locator('[data-testid="application-step-2"]').wait_for(timeout=10000)
    await page.locator('[data-testid="resume-upload-input"]').set_input_files('/app/test_reports/dummy_resume.pdf')
    await page.locator('[data-testid="application-next-button"]').click()
    await page.locator('[data-testid="application-step-3"]').wait_for(timeout=10000)
    await page.locator('[data-testid="cover-letter-input"]').fill('Iteration 3 QA cover letter persistence check for TechNova.')
    await page.locator('[data-testid="application-back-button"]').click()
    await page.locator('[data-testid="application-step-2"]').wait_for(timeout=10000)
    await page.locator('[data-testid="application-next-button"]').click()
    assert await page.locator('[data-testid="cover-letter-input"]').input_value() == 'Iteration 3 QA cover letter persistence check for TechNova.'
    await page.locator('[data-testid="application-next-button"]').click()
    await page.locator('[data-testid="application-step-4"]').wait_for(timeout=10000)
    await page.locator('[data-testid="application-submit-button"]').click()
    await page.locator('[data-testid="application-success"]').wait_for(timeout=10000)
    await page.locator('[data-testid="track-application-button"]').click()
    await page.wait_for_url("**/applications", timeout=10000)
