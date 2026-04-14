// HD-2D Character Shader (Unity URP)
// Renders 2D sprites with rim lighting, outline, and depth write
// so they integrate with 3D backgrounds and depth-of-field post-processing.

Shader "HD2DRPG/HD2D_Character"
{
    Properties
    {
        _MainTex        ("Sprite Texture",  2D)    = "white" {}
        _Color          ("Tint",           Color) = (1,1,1,1)
        _OutlineColor   ("Outline Color",  Color) = (0,0,0,1)
        _OutlineWidth   ("Outline Width",  Range(0, 0.05)) = 0.01
        _RimColor       ("Rim Light Color",Color) = (1,0.9,0.7,1)
        _RimPower       ("Rim Power",      Range(0.1, 8.0)) = 3.0
        _Brightness     ("Brightness",     Range(0.5, 2.0)) = 1.0
        [Toggle] _DepthWrite ("Write Depth", Float) = 1
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "TransparentCutout"
            "Queue" = "Geometry+1"
            "RenderPipeline" = "UniversalPipeline"
        }

        // ── Pass 1: Outline (slightly enlarged, solid outline color) ──
        Pass
        {
            Name "Outline"
            Cull Front
            ZWrite On
            Blend SrcAlpha OneMinusSrcAlpha

            HLSLPROGRAM
            #pragma vertex OutlineVert
            #pragma fragment OutlineFrag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes { float4 posOS : POSITION; float2 uv : TEXCOORD0; };
            struct Varyings   { float4 posCS : SV_POSITION; float2 uv : TEXCOORD0; };

            TEXTURE2D(_MainTex); SAMPLER(sampler_MainTex);
            float4 _MainTex_ST;
            float4 _OutlineColor;
            float  _OutlineWidth;

            Varyings OutlineVert(Attributes IN)
            {
                Varyings OUT;
                float4 pos = IN.posOS;
                pos.xy += normalize(pos.xy) * _OutlineWidth;
                OUT.posCS = TransformObjectToHClip(pos.xyz);
                OUT.uv = TRANSFORM_TEX(IN.uv, _MainTex);
                return OUT;
            }

            half4 OutlineFrag(Varyings IN) : SV_Target
            {
                half4 tex = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, IN.uv);
                clip(tex.a - 0.5);
                return _OutlineColor;
            }
            ENDHLSL
        }

        // ── Pass 2: Main sprite with rim lighting ──
        Pass
        {
            Name "Sprite"
            Cull Off
            ZWrite On
            Blend SrcAlpha OneMinusSrcAlpha

            HLSLPROGRAM
            #pragma vertex SpriteVert
            #pragma fragment SpriteFrag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Attributes
            {
                float4 posOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 posCS : SV_POSITION;
                float2 uv    : TEXCOORD0;
                float3 worldNormal : TEXCOORD1;
                float3 worldPos    : TEXCOORD2;
            };

            TEXTURE2D(_MainTex); SAMPLER(sampler_MainTex);
            float4 _MainTex_ST;
            float4 _Color;
            float4 _RimColor;
            float  _RimPower;
            float  _Brightness;

            Varyings SpriteVert(Attributes IN)
            {
                Varyings OUT;
                OUT.posCS       = TransformObjectToHClip(IN.posOS.xyz);
                OUT.uv          = TRANSFORM_TEX(IN.uv, _MainTex);
                OUT.worldNormal = TransformObjectToWorldNormal(IN.normalOS);
                OUT.worldPos    = TransformObjectToWorld(IN.posOS.xyz);
                return OUT;
            }

            half4 SpriteFrag(Varyings IN) : SV_Target
            {
                half4 tex = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, IN.uv);
                clip(tex.a - 0.1);

                half4 color = tex * _Color;

                // Simple rim lighting using main directional light direction
                float3 viewDir = normalize(_WorldSpaceCameraPos - IN.worldPos);
                float rim = 1.0 - saturate(dot(normalize(IN.worldNormal), viewDir));
                rim = pow(rim, _RimPower);
                color.rgb += _RimColor.rgb * rim * _RimColor.a;

                color.rgb *= _Brightness;
                return color;
            }
            ENDHLSL
        }
    }

    FallBack "Sprites/Default"
}
