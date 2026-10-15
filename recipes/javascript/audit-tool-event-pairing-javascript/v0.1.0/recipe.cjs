'use strict';

const fs = require('node:fs');

function main() {
  let output;

  try {
    if (process.argv.length !== 2) {
      throw new Error();
    }

    const buffer = Buffer.alloc(65537);
    let used = 0;

    while (used < buffer.length) {
      const count = fs.readSync(0, buffer, used, buffer.length - used, null);
      if (count === 0) break;
      used += count;
    }

    if (used > 65536) {
      throw new Error();
    }

    const decoder = new TextDecoder('utf-8', {
      fatal: true,
      ignoreBOM: true
    });
    const text = decoder.decode(buffer.subarray(0, used));
    const events = JSON.parse(text);

    if (!Array.isArray(events) || events.length > 100) {
      throw new Error();
    }

    for (const event of events) {
      if (
        event === null ||
        typeof event !== 'object' ||
        Array.isArray(event) ||
        (event.kind !== 'request' && event.kind !== 'result') ||
        typeof event.id !== 'string' ||
        event.id.length === 0 ||
        event.id.length > 80
      ) {
        throw new Error();
      }
    }

    const pending = new Set();
    const unmatchedResults = [];
    const repeatedRequests = [];

    for (let index = 0; index < events.length; index += 1) {
      const event = events[index];
      const position = index + 1;

      if (event.kind === 'request') {
        if (pending.has(event.id)) {
          repeatedRequests.push(position);
        } else {
          pending.add(event.id);
        }
      } else if (!pending.delete(event.id)) {
        unmatchedResults.push(position);
      }
    }

    output = JSON.stringify({
      unanswered: Array.from(pending).sort(),
      unmatched_results: unmatchedResults,
      repeated_requests: repeatedRequests
    });
  } catch {
    process.stderr.write('error: invalid input\n', () => process.exit(2));
    return;
  }

  // Output-write failures are deliberately outside the input-error handler.
  process.stdout.write(output + '\n');
}

main();
