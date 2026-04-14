using UnityEngine;
using System.Collections;

namespace HD2DRPG
{
    /// <summary>
    /// Handles visual feedback during combat: screen shake, flash, hit sparks.
    /// Stubbed for now — wire up particle systems and animator controllers here.
    /// </summary>
    public class CombatAnimator : MonoBehaviour
    {
        [Header("Screen Shake")]
        public float shakeDuration = 0.15f;
        public float shakeMagnitude = 0.08f;

        Camera _cam;

        void Awake() => _cam = Camera.main;

        public IEnumerator PlayAttack(PartyMember attacker, EnemyCombatState target)
        {
            yield return ScreenShake();
            yield return new WaitForSeconds(0.3f);
        }

        public IEnumerator PlaySkill(PartyMember attacker, EnemyCombatState target, SkillData skill)
        {
            // TODO: spawn element-specific particle at target position
            yield return ScreenShake();
            yield return new WaitForSeconds(0.5f);
        }

        public IEnumerator PlayEnemyAttack(EnemyCombatState enemy)
        {
            yield return ScreenShake();
            yield return new WaitForSeconds(0.3f);
        }

        IEnumerator ScreenShake()
        {
            if (_cam == null) yield break;
            Vector3 origin = _cam.transform.localPosition;
            float elapsed = 0f;

            while (elapsed < shakeDuration)
            {
                _cam.transform.localPosition = origin + (Vector3)Random.insideUnitCircle * shakeMagnitude;
                elapsed += Time.deltaTime;
                yield return null;
            }
            _cam.transform.localPosition = origin;
        }
    }
}
