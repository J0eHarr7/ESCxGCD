const puppeteer = require("puppeteer");

const APP_URL = "http://app:5000";

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runBot() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox"]
    });

    const page = await browser.newPage();

    // Set sensitive admin cookie (FLAG)
    await page.setCookie({
        name: "FLAG",
        value: "ESECxGCD{STORED_XSS_ADMIN_COMPROMISED}",
        domain: "app",
        httpOnly: false
    });

    // Login as admin
    await page.goto(APP_URL);
    await page.type('input[name=username]', 'admin');
    await page.type('input[name=password]', 'admin123');
    await page.click('button[type=submit]');

    await sleep(1000);

    // Visit comments page
    await page.goto(`${APP_URL}/comments`);

    await sleep(5000);

    await browser.close();
}

setInterval(runBot, 15000);
