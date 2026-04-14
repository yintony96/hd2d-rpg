// HD-2D Background Shader (Unity URP)
// For 3D environment meshes rendered behind 2D sprites.
// Flat ambient + dynamic point lights, slight desaturation for depth feel.

Shader "HD2DRPG/HD2D_Background"
{
    Properties
    {
        _MainTex      ("Albedo",          2D)    = "white" {}
        _Color        ("Tint",           Color) = (1,1,1,1)
        _AmbientColor ("Ambient Color",  Color) = (0.15,0.1,0.2,1)
        _Saturation   ("Saturation",     Range(0,2)) = 0.8
        _FogColor     ("Distance Fog",   Color) = (0.08,0.06,0.12,1)
        _FogStart     ("Fog Start",      Float) = 15.0
        _FogEnd       ("Fog End",        Float) = 40.0
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }

        Pass
        {
            Name "Background"
            ZWrite On
            Cull Back

            HLSLPROGRAM
            #pragma vertex BgVert
            #pragma fragment BgFrag
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Attributes
            {
                float4 posOS   : POSITION;
                float3 normalOS: NORMAL;
                float2 uv      : TEXCOORD0;
            };

            struct Varyings
            {
                float4 posCS    : SV_POSITION;
                float2 uv       : TEXCOORD0;
                float3 worldPos : TEXCOORD1;
                float3 worldNormal : TEXCOORD2;
            };

            TEXTURE2D(_MainTex); SAMPLER(sampler_MainTex);
            float4 _MainTex_ST;
            float4 _Color;
            float4 _AmbientColor;
            float  _Saturation;
            float4 _FogColor;
            float  _FogStart;
            float  _FogEnd;

            Varyings BgVert(Attributes IN)
            {
                Varyings OUT;
                OUT.posCS       = TransformObjectToHClip(IN.posOS.xyz);
                OUT.uv          = TRANSFORM_TEX(IN.uv, _MainTex);
                OUT.worldPos    = TransformObjectToWorld(IN.posOS.xyz);
                OUT.worldNormal = TransformObjectToWorldNormal(IN.normalOS);
                return OUT;
            }

            half4 BgFrag(Varyings IN) : SV_Target
            {
                half4 tex = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, IN.uv) * _Color;

                // Ambient
                float3 color = tex.rgb + _AmbientColor.rgb;

                // Additional point lights (torches, magic sources)
                #ifdef _ADDITIONAL_LIGHTS
                uint lightCount = GetAdditionalLightsCount();
                for (uint i = 0; i < lightCount; ++i)
                {
                    Light light = GetAdditionalLight(i, IN.worldPos);
                    float NdotL = saturate(dot(IN.worldNormal, light.direction));
                    color += light.color * light.distanceAttenuation * NdotL * 0.6;
                }
                #endif

                // Saturation adjustment (slightly desaturate background vs sprites)
                float luminance = dot(color, float3(0.299, 0.587, 0.114));
                color = lerp(float3(luminance, luminance, luminance), color, _Saturation);

                // Distance fog
                float camDist = length(_WorldSpaceCameraPos - IN.worldPos);
                float fogFactor = saturate((camDist - _FogStart) / (_FogEnd - _FogStart));
                color = lerp(color, _FogColor.rgb, fogFactor);

                return half4(color, 1.0);
            }
            ENDHLSL
        }
    }

    FallBack "Universal Render Pipeline/Lit"
}
