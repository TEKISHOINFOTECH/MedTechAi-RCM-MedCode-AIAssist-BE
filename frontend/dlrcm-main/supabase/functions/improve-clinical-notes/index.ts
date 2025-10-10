import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const { clinicalNotes } = await req.json();

    if (!clinicalNotes || clinicalNotes.trim().length === 0) {
      return new Response(
        JSON.stringify({ error: "Clinical notes are required" }),
        {
          status: 400,
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

    const prompt = `You are a medical documentation expert specializing in clinical note improvement and SOAP format standardization.

ORIGINAL CLINICAL NOTES:
${clinicalNotes}

TASK: Rewrite and improve these clinical notes using the professional SOAP (Subjective, Objective, Assessment, Plan) format.

SOAP FORMAT GUIDELINES:

**S (Subjective):**
- Patient's chief complaint in their own words
- History of present illness (HPI)
- Relevant symptoms and their characteristics (onset, duration, severity, factors)
- Past medical history relevant to current visit
- Patient concerns and questions

**O (Objective):**
- Vital signs (if available or reasonable to include)
- Physical examination findings
- Laboratory results (if mentioned)
- Imaging or diagnostic test results
- Observable patient presentation

**A (Assessment):**
- Primary diagnosis or differential diagnoses
- Clinical impression based on S and O
- Problem list with ICD-10 codes if identifiable
- Severity and complexity assessment
- Risk factors and complications

**P (Plan):**
- Treatment interventions (medications, procedures)
- Diagnostic tests ordered
- Referrals to specialists
- Patient education provided
- Follow-up instructions and timeline
- Preventive care recommendations

REQUIREMENTS:
1. Maintain all clinically relevant information from the original notes
2. Add professional medical terminology where appropriate
3. Organize information logically within SOAP structure
4. Use complete, grammatically correct sentences
5. Include specific measurements, dosages, and timeframes when available
6. Make reasonable clinical inferences only when strongly supported by the original text
7. Preserve the patient's actual symptoms and the provider's actual findings
8. Format for readability with clear section headers

Output the improved notes in clean, professional SOAP format. Do not include explanations or meta-commentary.`;

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
            content: "You are a medical documentation expert. Rewrite clinical notes in professional SOAP format while preserving all clinical information."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: 0.3,
        max_tokens: 2000,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("OpenAI API error:", errorText);
      return new Response(
        JSON.stringify({ error: "Failed to improve notes" }),
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
    const improvedNotes = data.choices[0]?.message?.content || clinicalNotes;

    return new Response(
      JSON.stringify({ improvedNotes }),
      {
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  } catch (error) {
    console.error("Error in improve-clinical-notes:", error);
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
