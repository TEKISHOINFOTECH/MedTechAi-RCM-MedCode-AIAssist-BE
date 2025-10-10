import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

interface ICDSuggestion {
  code: string;
  description: string;
  confidence: number;
  rationale: string;
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
    const { clinicalNotes, patientHistory } = await req.json();

    if (!clinicalNotes || clinicalNotes.trim().length === 0) {
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

    const historyText = patientHistory && patientHistory.length > 0
      ? patientHistory.map((h: PatientHistory) =>
          `${h.date}: ${h.diagnosis} (${h.icdCode}) - ${h.provider}`
        ).join('\n')
      : 'No prior medical history available';

    const prompt = `You are a medical coding expert. Based on the following clinical notes and patient medical history, suggest the most appropriate ICD-10 codes considering Guidelines combination.

Clinical Notes:
${clinicalNotes}

Patient Medical History:
${historyText}

Consider the patient's historical conditions when suggesting current diagnosis codes. Chronic conditions may recur, and new diagnoses should be evaluated in context of past medical history.

Provide up to 10 most relevant ICD-10 codes with descriptions. For each code, include:
1. The ICD-10 code
2. A clear description
3. Confidence level (0-100)
4. Brief rationale for why this code is relevant, considering both current notes and patient history

Respond ONLY with valid JSON in this exact format:
{
  "suggestions": [
    {
      "code": "E11.9",
      "description": "Type 2 diabetes mellitus without complications",
      "confidence": 95,
      "rationale": "Patient presents with symptoms consistent with diabetes, has history of diabetes"
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
            content: "You are a medical coding expert specializing in ICD-10 codes. Always respond with valid JSON only."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: 0.8,
        max_tokens: 1000,
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
    
    let suggestions: ICDSuggestion[] = [];
    try {
      const parsed = JSON.parse(content);
      suggestions = parsed.suggestions || [];
    } catch (parseError) {
      console.error("Failed to parse LLM response:", parseError);
      const codeMatches = content.match(/[A-Z]\d{2}\.?\d*/g) || [];
      suggestions = codeMatches.slice(0, 5).map((code: string) => ({
        code,
        description: "Code suggested by AI",
        confidence: 70,
        rationale: "Extracted from clinical notes analysis"
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
    console.error("Error in suggest-icd-codes:", error);
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
