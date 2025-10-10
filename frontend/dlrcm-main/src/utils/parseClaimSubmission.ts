interface ParsedClaimData {
  claimNumber?: string;
  patientName?: string;
  patientId?: string;
  dateOfService?: string;
  provider?: string;
  totalAmount?: number;
  diagnosis?: string;
  procedures?: string;
  clinicalNotes?: string;
}

export function parseClaimSubmissionFile(fileContent: string): ParsedClaimData {
  const result: ParsedClaimData = {};

  const lines = fileContent.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    const lowerLine = line.toLowerCase();

    if (lowerLine.includes('claim number') || lowerLine.includes('claim#') || lowerLine.includes('claim id')) {
      result.claimNumber = extractValue(line) || extractValue(lines[i + 1]);
    }

    if (lowerLine.includes('patient name') || lowerLine.includes('patient:')) {
      result.patientName = extractValue(line) || extractValue(lines[i + 1]);
    }

    if (lowerLine.includes('patient id') || lowerLine.includes('member id') || lowerLine.includes('patient number')) {
      result.patientId = extractValue(line) || extractValue(lines[i + 1]);
    }

    if (lowerLine.includes('date of service') || lowerLine.includes('service date') || lowerLine.includes('dos:')) {
      const dateStr = extractValue(line) || extractValue(lines[i + 1]);
      result.dateOfService = parseDate(dateStr);
    }

    if (lowerLine.includes('provider') || lowerLine.includes('physician') || lowerLine.includes('doctor')) {
      result.provider = extractValue(line) || extractValue(lines[i + 1]);
    }

    if (lowerLine.includes('total amount') || lowerLine.includes('charge amount') || lowerLine.includes('billed amount')) {
      const amountStr = extractValue(line) || extractValue(lines[i + 1]);
      result.totalAmount = parseAmount(amountStr);
    }

    if (lowerLine.includes('diagnosis') || lowerLine.includes('icd')) {
      let diagnosisText = extractValue(line) || '';
      if (!diagnosisText && i + 1 < lines.length) {
        diagnosisText = lines[i + 1].trim();
      }
      result.diagnosis = diagnosisText;
    }

    if (lowerLine.includes('procedure') || lowerLine.includes('cpt') || lowerLine.includes('service code')) {
      let procedureText = extractValue(line) || '';
      if (!procedureText && i + 1 < lines.length) {
        procedureText = lines[i + 1].trim();
      }
      result.procedures = procedureText;
    }

    if (lowerLine.includes('clinical notes') || lowerLine.includes('notes') || lowerLine.includes('observations') || lowerLine.includes('comments')) {
      let notesText = extractValue(line) || '';
      let j = i + 1;
      while (j < lines.length && lines[j].trim() && !lines[j].includes(':')) {
        notesText += ' ' + lines[j].trim();
        j++;
      }
      result.clinicalNotes = notesText.trim();
    }
  }

  return result;
}

function extractValue(line: string): string {
  if (!line) return '';

  const colonIndex = line.indexOf(':');
  if (colonIndex !== -1) {
    return line.substring(colonIndex + 1).trim();
  }

  const dashIndex = line.indexOf('-');
  if (dashIndex !== -1) {
    return line.substring(dashIndex + 1).trim();
  }

  return line.trim();
}

function parseDate(dateStr: string): string {
  if (!dateStr) return '';

  dateStr = dateStr.replace(/[^\d\/\-\.]/g, '');

  const formats = [
    /(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})/,
    /(\d{1,2})[-\/](\d{1,2})[-\/](\d{4})/,
    /(\d{1,2})[-\/](\d{1,2})[-\/](\d{2})/,
  ];

  for (const format of formats) {
    const match = dateStr.match(format);
    if (match) {
      if (match[1].length === 4) {
        const year = match[1];
        const month = match[2].padStart(2, '0');
        const day = match[3].padStart(2, '0');
        return `${year}-${month}-${day}`;
      } else {
        let year = match[3];
        if (year.length === 2) {
          year = '20' + year;
        }
        const month = match[1].padStart(2, '0');
        const day = match[2].padStart(2, '0');
        return `${year}-${month}-${day}`;
      }
    }
  }

  return dateStr;
}

function parseAmount(amountStr: string): number {
  if (!amountStr) return 0;

  const cleaned = amountStr.replace(/[^\d.]/g, '');
  const amount = parseFloat(cleaned);

  return isNaN(amount) ? 0 : amount;
}
