using UnityEngine;
using System.Collections.Generic;
using System.Linq;

namespace HD2DRPG
{
    public enum CombatantType { Player, Enemy }

    public class CombatTurn
    {
        public CombatantType type;
        public PartyMember player;   // set if type == Player
        public EnemyCombatState enemy; // set if type == Enemy
        public int speed;

        public string DisplayName => type == CombatantType.Player
            ? player.data.characterName
            : enemy.data.enemyName;

        public Sprite Portrait => type == CombatantType.Player
            ? player.data.portrait
            : enemy.data.sprite;
    }

    /// <summary>
    /// Builds and manages the turn order for a combat encounter.
    /// Octopath-style: speed-based order, updated after boost actions.
    /// </summary>
    public class TurnQueue
    {
        List<CombatTurn> _queue = new();

        public IReadOnlyList<CombatTurn> Queue => _queue;

        public void Build(List<PartyMember> party, List<EnemyCombatState> enemies)
        {
            _queue.Clear();

            foreach (var p in party)
            {
                if (!p.IsAlive) continue;
                _queue.Add(new CombatTurn
                {
                    type = CombatantType.Player,
                    player = p,
                    speed = p.spd + Random.Range(0, 3) // slight jitter
                });
            }

            foreach (var e in enemies)
            {
                if (!e.IsAlive) continue;
                if (e.isBreaking) continue; // broken enemies skip turn
                _queue.Add(new CombatTurn
                {
                    type = CombatantType.Enemy,
                    enemy = e,
                    speed = 10 + Random.Range(0, 5) // base enemy speed
                });
            }

            _queue = _queue.OrderByDescending(t => t.speed).ToList();
        }

        public CombatTurn Peek() => _queue.Count > 0 ? _queue[0] : null;

        public CombatTurn Dequeue()
        {
            if (_queue.Count == 0) return null;
            var t = _queue[0];
            _queue.RemoveAt(0);
            return t;
        }

        public bool IsEmpty => _queue.Count == 0;

        /// <summary>
        /// When a player boosts (spending BP), re-sort to reflect boosted action priority.
        /// </summary>
        public void OnBoost(PartyMember member, int bpSpent)
        {
            // Boost delays subsequent turns slightly (cost of power)
            var existing = _queue.Where(t => t.type == CombatantType.Player && t.player == member).ToList();
            foreach (var t in existing)
                t.speed = Mathf.Max(0, t.speed - bpSpent * 2);
            _queue = _queue.OrderByDescending(t => t.speed).ToList();
        }
    }
}
