'use strict';

import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import chromium from '@sparticuz/chromium';

const maxResultLength = 6291556;
function resultLength(r) {
  return Buffer.byteLength(JSON.stringify(r));
}

puppeteer.use(StealthPlugin());

export async function main(url, log={}) {
  const timeBase = Date.now();
  log.url = url;
  log.events = [];
  function logEvent(event) {
    log.events.push({time: (Date.now() - timeBase) / 1000, ...event});
  }

  const browser = await puppeteer.launch({
    args: chromium.args.concat([
      '--disable-file-system',
    ]),
    defaultViewport: chromium.defaultViewport,
    executablePath: await chromium.executablePath(),
    headless: chromium.headless,
  });
  logEvent({event: 'launch'});

  const page = await browser.newPage();
  const cdp = await page.target().createCDPSession();
  async function getContent() {
    const {documents, strings} = await cdp.send('DOMSnapshot.captureSnapshot', {computedStyles: []});
    return documents[0].layout.text.map(i => i == -1 ? '' : strings[i]).filter(i => i).join(' ');
  }
  logEvent({event: 'newPage'});

  let progressTimeout = setTimeout(async function f() {
    try {
      logEvent({event: 'progress', length: (await getContent()).length});
    } catch {}
    progressTimeout = setTimeout(f, 500);
  }, 500);

  page.on('load', () => logEvent({event: 'load'}));
  page.on('domcontentloaded', () => logEvent({event: 'domcontentloaded'}));
  try {
    await page.goto(url, {timeout: 30000, waitUntil: ['load', 'domcontentloaded', 'networkidle0']});
  } catch {}
  logEvent({event: 'goto'});

  await new Promise(r => setTimeout(r, 3000));
  const content = await getContent();
  clearTimeout(progressTimeout);
  logEvent({event: 'captureSnapshot', length: content.length});

  let title = await page.title();
  await browser.close();
  logEvent({event: 'close'});

  console.log(JSON.stringify(log, null, 2));

  const result = {
    data: {url, title, content},
    truncated: false,
    template: [
      {field: 'url', name: 'URL', type: 'inline'},
      {field: 'title', name: 'Title', type: 'inline'},
      {field: 'content', name: 'Content', type: 'block'},
    ],
  };
  if (resultLength(result) > maxResultLength) {
    result.truncated = true;
    result.data.content = '';
    let left = 0;
    let right = content.length;
    while (left + 1 < right) {
      const mid = Math.floor((left + right) / 2);
      result.data.content = content.slice(0, mid);
      if (resultLength(result) > maxResultLength) {
        right = mid;
      } else {
        left = mid;
      }
    }
    result.data.content = content.slice(0, left);
  }
  return result;
}

export async function handler(event, context) {
  return await main(JSON.parse(event.body).url, {event, context});
}
