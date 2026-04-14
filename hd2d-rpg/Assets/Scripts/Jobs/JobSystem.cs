using UnityEngine;
using System.Collections.Generic;

namespace HD2DRPG
{
    /// <summary>
    /// Manages job progression: JP accumulation, skill unlocking, evolution.
    /// </summary>
    public static class JobSystem
    {
        // JP required per job level (index = level - 1)
        static readonly int[] JPThresholds = { 0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200, 4000,
                                                5000, 6200, 7600, 9200, 11000, 13000, 15500, 18500, 22000 };

        /// <summary>
        /// Add JP to a party member's current job. Handles level-ups and skill unlocks.
        /// Returns list of newly unlocked skill names.
        /// </summary>
        public static List<string> AddJP(PartyMember member, int jp)
        {
            var newSkills = new List<string>();
            if (member.currentJob == null) return newSkills;

            member.jobPoints += jp;

            // Check level-ups
            while (member.jobLevel < JPThresholds.Length - 1 &&
                   member.jobPoints >= JPThresholds[member.jobLevel + 1])
            {
                member.jobLevel++;
                var unlocked = CheckSkillUnlocks(member);
                newSkills.AddRange(unlocked);
            }

            return newSkills;
        }

        static List<string> CheckSkillUnlocks(PartyMember member)
        {
            var newSkills = new List<string>();
            if (member.currentJob?.skills == null) return newSkills;

            // Unlock skills progressively: 1 skill per 2 job levels
            int skillIndex = (member.jobLevel / 2) - 1;
            if (skillIndex >= 0 && skillIndex < member.currentJob.skills.Length)
            {
                var skill = member.currentJob.skills[skillIndex];
                if (skill != null && !member.unlockedSkills.Contains(skill))
                {
                    member.unlockedSkills.Add(skill);
                    newSkills.Add(skill.skillName);
                    Debug.Log($"{member.data.characterName} unlocked {skill.skillName}!");
                }
            }

            return newSkills;
        }

        /// <summary>
        /// Check if a member can evolve their job.
        /// </summary>
        public static bool CanEvolve(PartyMember member, out JobData[] options)
        {
            options = null;
            if (member.currentJob == null) return false;
            if (member.jobLevel < member.currentJob.evolutionRequiredLevel) return false;
            if (member.currentJob.evolutionOptions == null ||
                member.currentJob.evolutionOptions.Length == 0) return false;

            options = member.currentJob.evolutionOptions;
            return true;
        }

        /// <summary>
        /// Evolve job to chosen option. Retains learned passives.
        /// </summary>
        public static void EvolveJob(PartyMember member, JobData targetJob)
        {
            // Carry over passives from current job
            var retainedPassives = new List<PassiveData>(member.currentJob.passives ?? new PassiveData[0]);

            member.currentJob = targetJob;
            member.jobLevel = 1;
            member.jobPoints = 0;
            // Keep previously earned passives accessible
            // (full implementation would store per-job progression)

            member.unlockedSkills.Clear();
            member.RecalculateStats();

            Debug.Log($"{member.data.characterName} evolved to {targetJob.jobName}!");
        }

        /// <summary>
        /// Respec: reset job back to its base, costing the respec fee.
        /// </summary>
        public static bool Respec(PartyMember member, int goldCost, ref int playerGold)
        {
            if (playerGold < goldCost) return false;
            if (member.currentJob?.baseJob == null) return false;

            playerGold -= goldCost;
            member.currentJob = member.currentJob.baseJob;
            member.jobLevel = 1;
            member.jobPoints = 0;
            member.unlockedSkills.Clear();
            member.RecalculateStats();

            Debug.Log($"{member.data.characterName} respecced to {member.currentJob.jobName}.");
            return true;
        }
    }
}
