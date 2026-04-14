using UnityEngine;
using System.Collections.Generic;

namespace HD2DRPG
{
    /// <summary>
    /// Runtime state for a character in the party.
    /// CharacterData = template; PartyMember = live instance with HP/MP/JP etc.
    /// </summary>
    [System.Serializable]
    public class PartyMember
    {
        public CharacterData data;

        // Current stats (computed from data + job + level)
        public int level = 1;
        public int currentHP;
        public int currentMP;
        public int maxHP;
        public int maxMP;
        public int str, def, spd, mnd;

        // Boost Points (0–3, gained each turn)
        public int boostPoints;
        public const int MaxBoostPoints = 3;

        // Job system
        public JobData currentJob;
        public int jobLevel;
        public int jobPoints;
        public int jobPointsToNextLevel = 100;

        // Unlocked skills for this job
        public List<SkillData> unlockedSkills = new();

        // Active status effects
        public List<ActiveStatusEffect> statusEffects = new();

        // Turn order (recomputed each round)
        [System.NonSerialized] public int turnOrderValue;
        [System.NonSerialized] public bool hasTakenTurn;

        public bool IsAlive => currentHP > 0;
        public bool IsBreakable => false; // Players don't get broken, only enemies

        public void Initialize()
        {
            if (data == null) return;
            level = 1;
            currentJob = data.startingJob;
            RecalculateStats();
            currentHP = maxHP;
            currentMP = maxMP;
            boostPoints = 0;
        }

        public void RecalculateStats()
        {
            int lvl = level;
            maxHP  = Mathf.RoundToInt(data.baseHP  + data.hpGrowth  * (lvl - 1));
            maxMP  = Mathf.RoundToInt(data.baseMP  + data.mpGrowth  * (lvl - 1));
            str    = Mathf.RoundToInt(data.baseSTR + data.strGrowth * (lvl - 1));
            def    = Mathf.RoundToInt(data.baseDEF + data.defGrowth * (lvl - 1));
            spd    = Mathf.RoundToInt(data.baseSPD + data.spdGrowth * (lvl - 1));
            mnd    = Mathf.RoundToInt(data.baseMND + data.mndGrowth * (lvl - 1));

            if (currentJob != null)
            {
                maxHP += currentJob.hpModifier;
                maxMP += currentJob.mpModifier;
                str   += currentJob.strModifier;
                def   += currentJob.defModifier;
                spd   += currentJob.spdModifier;
                mnd   += currentJob.mndModifier;
            }
        }

        public void StartTurn()
        {
            // Gain 1 BP per turn, cap at max
            boostPoints = Mathf.Min(boostPoints + 1, MaxBoostPoints);
            hasTakenTurn = false;

            // Tick status effects
            for (int i = statusEffects.Count - 1; i >= 0; i--)
            {
                statusEffects[i].turnsRemaining--;
                if (statusEffects[i].turnsRemaining <= 0)
                    statusEffects.RemoveAt(i);
            }
        }

        public void TakeDamage(int amount)
        {
            currentHP = Mathf.Max(0, currentHP - amount);
        }

        public void RestoreHP(int amount)
        {
            currentHP = Mathf.Min(maxHP, currentHP + amount);
        }

        public void UseMP(int amount)
        {
            currentMP = Mathf.Max(0, currentMP - amount);
        }
    }

    [System.Serializable]
    public class ActiveStatusEffect
    {
        public StatusEffectData data;
        public int turnsRemaining;
    }
}
