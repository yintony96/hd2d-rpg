using UnityEngine;
using System.Collections.Generic;

namespace HD2DRPG
{
    public enum RoomType
    {
        Combat,
        Elite,
        Event,
        Shop,
        Rest,
        Puzzle,
        Secret,
        Boss
    }

    [System.Serializable]
    public class FloorNode
    {
        public int floor;
        public RoomType roomType;
        public List<int> nextNodeIndices = new(); // branching connections
        public bool visited;
        public bool isStart;
        public bool isBoss;
    }

    /// <summary>
    /// Generates a branching tower floor map.
    /// Seed-based: same seed → same layout (reproducible runs).
    /// </summary>
    public class TowerGenerator : MonoBehaviour
    {
        [Header("Config")]
        public int totalFloors = 20;
        public int branchWidth = 3;    // Max paths in parallel

        [Header("Room Weights (must sum to ~100)")]
        public int weightCombat  = 40;
        public int weightElite   = 15;
        public int weightEvent   = 15;
        public int weightShop    = 10;
        public int weightRest    = 10;
        public int weightPuzzle  = 5;
        public int weightSecret  = 5;

        List<FloorNode> _nodes = new();
        int _seed;

        public IReadOnlyList<FloorNode> Nodes => _nodes;

        public void Generate(int seed)
        {
            _seed = seed;
            Random.InitState(seed);
            _nodes.Clear();

            // Floor 0: entry
            var start = new FloorNode { floor = 0, roomType = RoomType.Rest, isStart = true };
            _nodes.Add(start);

            // Floors 1 .. totalFloors-1: branching
            int prevLayerStart = 0;
            int prevLayerCount = 1;

            for (int f = 1; f < totalFloors; f++)
            {
                bool isBossFloor = (f == totalFloors - 1);
                int nodeCount = isBossFloor ? 1 : Random.Range(2, branchWidth + 1);

                int layerStart = _nodes.Count;
                for (int n = 0; n < nodeCount; n++)
                {
                    var node = new FloorNode
                    {
                        floor = f,
                        roomType = isBossFloor ? RoomType.Boss : PickRoomType(),
                        isBoss = isBossFloor
                    };
                    _nodes.Add(node);
                }

                // Connect previous layer → this layer
                for (int p = prevLayerStart; p < prevLayerStart + prevLayerCount; p++)
                {
                    // Each previous node connects to 1–2 nodes in this layer
                    int connectCount = isBossFloor ? 1 : Random.Range(1, 3);
                    var picked = new HashSet<int>();
                    for (int c = 0; c < connectCount; c++)
                    {
                        int target = layerStart + Random.Range(0, nodeCount);
                        if (picked.Add(target))
                            _nodes[p].nextNodeIndices.Add(target);
                    }
                }

                prevLayerStart = layerStart;
                prevLayerCount = nodeCount;
            }
        }

        RoomType PickRoomType()
        {
            int roll = Random.Range(0, 100);
            int cumulative = 0;

            if ((cumulative += weightCombat) > roll) return RoomType.Combat;
            if ((cumulative += weightElite)  > roll) return RoomType.Elite;
            if ((cumulative += weightEvent)  > roll) return RoomType.Event;
            if ((cumulative += weightShop)   > roll) return RoomType.Shop;
            if ((cumulative += weightRest)   > roll) return RoomType.Rest;
            if ((cumulative += weightPuzzle) > roll) return RoomType.Puzzle;
            return RoomType.Secret;
        }

        public FloorNode GetStartNode() => _nodes.Count > 0 ? _nodes[0] : null;
        public FloorNode GetNode(int index) => _nodes[index];
    }
}
