using UnityEngine;

namespace HD2DRPG
{
    /// <summary>
    /// Smooth camera follow for the hub overworld.
    /// Attach to the Player — moves the main camera to track it.
    /// </summary>
    public class CameraFollow : MonoBehaviour
    {
        [Header("Follow Settings")]
        public float smoothSpeed = 5f;
        public Vector3 offset    = new Vector3(0, 7, -10);

        Camera _cam;

        void Start()
        {
            _cam = Camera.main;
            if (_cam != null)
                _cam.transform.position = transform.position + offset;
        }

        void LateUpdate()
        {
            if (_cam == null) return;
            Vector3 target = transform.position + offset;
            _cam.transform.position = Vector3.Lerp(_cam.transform.position, target, smoothSpeed * Time.deltaTime);
        }
    }
}
