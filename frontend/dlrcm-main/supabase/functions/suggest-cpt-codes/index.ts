import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

interface CPTSuggestion {
  code: string;
  description: string;
  category: string;
  confidence: number;
  rationale: string;
}

interface ICDCode {
  code: string;
  description: string;
}

interface PatientHistory {
  date: string;
  diagnosis: string;
  icdCode: string;
  provider: string;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const { icdCodes, patientHistory, clinicalNotes } = await req.json();

    if (!icdCodes || icdCodes.length === 0) {
      return new Response(
        JSON.stringify({ suggestions: [] }),
        {
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json",
          },
        }
      );
    }

    const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");
    if (!OPENAI_API_KEY) {
      console.error("OPENAI_API_KEY not configured");
      return new Response(
        JSON.stringify({ error: "LLM service not configured" }),
        {
          status: 500,
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json",
          },
        }
      );
    }

    const icdCodesText = icdCodes.map((icd: ICDCode) => `${icd.code} - ${icd.description}`).join('\n');
    
    const historyText = patientHistory && patientHistory.length > 0
      ? patientHistory.map((h: PatientHistory) => 
          `${h.date}: ${h.diagnosis} (${h.icdCode}) - ${h.provider}`
        ).join('\n')
      : 'No prior medical history available';

    const prompt = `You are a medical coding expert specializing in CPT (Current Procedural Terminology) codes. Based on the diagnosis codes (ICD-10) and patient medical history, suggest the most appropriate CPT procedure codes consider Guidelines combination.

Diagnosis Codes (ICD-10):
${icdCodesText}

Patient Medical History:
${historyText}

${clinicalNotes ? `Clinical Notes:\n${clinicalNotes}\n\n` : ''}
Consider:
1. The patient's current diagnosis codes
2. Their historical medical conditions and treatments
3. Standard procedures typically performed for these conditions
4. Appropriate evaluation and management (E&M) codes
5. Any necessary diagnostic tests or therapeutic procedures

Provide up to 10 most relevant CPT codes. For each code, include:
1. The CPT code (5-digit numeric code)
2. A clear description of the procedure or service
3. Category (e.g., "Evaluation & Management", "Laboratory", "Radiology", "Surgery", "Medicine")
4. Confidence level (0-100)
5. Brief rationale considering both current diagnosis and patient history

Respond ONLY with valid JSON in this exact format:
{
  "suggestions": [
    {
      "code": "99214",
      "description": "Office visit, established patient, moderate complexity",
      "category": "Evaluation & Management",
      "confidence": 95,
      "rationale": "Appropriate for follow-up of chronic conditions with patient's history of diabetes and hypertension"
    }
  ]
}`;

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content: "You are a medical coding expert specializing in CPT codes. Always respond with valid JSON only. Consider patient history when making suggestions."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: 0.2,
        max_tokens: 1500,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("OpenAI API error:", errorText);
      return new Response(
        JSON.stringify({ error: "Failed to get suggestions from LLM" }),
        {
          status: 500,
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json",
          },
        }
      );
    }

    const data = await response.json();
    const content = data.choices[0]?.message?.content || "";
    
    let suggestions: CPTSuggestion[] = [];
    try {
      const parsed = JSON.parse(content);
      suggestions = parsed.suggestions || [];
    } catch (parseError) {
      console.error("Failed to parse LLM response:", parseError);
      const codeMatches = content.match(/\d{5}/g) || [];
      suggestions = codeMatches.slice(0, 8).map((code: string) => ({
        code,
        description: "Procedure code suggested by AI",
        category: "General",
        confidence: 70,
        rationale: "Extracted from analysis"
      }));
    }

    return new Response(
      JSON.stringify({ suggestions }),
      {
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  } catch (error) {
    console.error("Error in suggest-cpt-codes:", error);
    return new Response(
      JSON.stringify({ error: error.message || "Internal server error" }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  }
});
