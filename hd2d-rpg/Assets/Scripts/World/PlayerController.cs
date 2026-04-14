using UnityEngine;

namespace HD2DRPG
{
    /// <summary>
    /// Top-down 8-directional player movement for overworld / hub scenes.
    /// Uses Unity's new Input System via direct keyboard polling as fallback.
    /// </summary>
    [RequireComponent(typeof(Rigidbody2D))]
    public class PlayerController : MonoBehaviour
    {
        [Header("Movement")]
        public float moveSpeed = 4f;
        public float runMultiplier = 1.6f;

        [Header("Animation")]
        public Animator animator;
        public SpriteRenderer spriteRenderer;

        Rigidbody2D _rb;
        Vector2 _input;
        bool _isRunning;
        bool _locked; // set true during dialogue/menus

        static readonly int AnimSpeed = Animator.StringToHash("Speed");
        static readonly int AnimDirX  = Animator.StringToHash("DirX");
        static readonly int AnimDirY  = Animator.StringToHash("DirY");

        void Awake() => _rb = GetComponent<Rigidbody2D>();

        public void Lock()   => _locked = true;
        public void Unlock() => _locked = false;

        void Update()
        {
            if (_locked) { _input = Vector2.zero; return; }

            _input.x = Input.GetAxisRaw("Horizontal");
            _input.y = Input.GetAxisRaw("Vertical");
            if (_input != Vector2.zero) _input.Normalize();

            _isRunning = Input.GetKey(KeyCode.LeftShift);

            // Flip sprite based on horizontal direction
            if (_input.x != 0 && spriteRenderer != null)
                spriteRenderer.flipX = _input.x < 0;

            // Drive animator
            if (animator != null)
            {
                animator.SetFloat(AnimSpeed, _input.magnitude);
                if (_input != Vector2.zero)
                {
                    animator.SetFloat(AnimDirX, _input.x);
                    animator.SetFloat(AnimDirY, _input.y);
                }
            }
        }

        void FixedUpdate()
        {
            float speed = moveSpeed * (_isRunning ? runMultiplier : 1f);
            _rb.linearVelocity = _input * speed;
        }
    }
}
