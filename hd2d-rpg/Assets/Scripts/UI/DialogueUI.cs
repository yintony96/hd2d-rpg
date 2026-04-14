using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;

namespace HD2DRPG
{
    /// <summary>
    /// Octopath-style dialogue box.
    /// Shows speaker portrait, name plate, and text with typewriter effect.
    /// Advances on Space/Enter/E.
    /// </summary>
    public class DialogueUI : MonoBehaviour
    {
        [Header("References")]
        public GameObject dialoguePanel;
        public Image portraitImage;
        public TextMeshProUGUI speakerNameText;
        public TextMeshProUGUI bodyText;
        public GameObject advanceIndicator; // blinking ▼ arrow

        [Header("Typewriter")]
        public float charsPerSecond = 40f;

        public bool IsActive { get; private set; }

        Coroutine _typewriter;

        // ──────────────────────────────────────────────────────────────

        public void Show(string speaker, Sprite portrait, string line)
        {
            IsActive = true;
            dialoguePanel.SetActive(true);
            advanceIndicator.SetActive(false);

            speakerNameText.text = speaker;
            if (portraitImage) portraitImage.sprite = portrait;

            if (_typewriter != null) StopCoroutine(_typewriter);
            _typewriter = StartCoroutine(Typewrite(line));
        }

        IEnumerator Typewrite(string fullText)
        {
            bodyText.text = "";
            foreach (char c in fullText)
            {
                bodyText.text += c;
                yield return new WaitForSeconds(1f / charsPerSecond);
            }
            advanceIndicator.SetActive(true);
            yield return WaitForAdvance();
            Close();
        }

        IEnumerator WaitForAdvance()
        {
            yield return null; // skip current frame
            while (!Input.GetKeyDown(KeyCode.E) &&
                   !Input.GetKeyDown(KeyCode.Space) &&
                   !Input.GetKeyDown(KeyCode.Return))
                yield return null;
        }

        public void SkipTypewriter()
        {
            if (_typewriter != null) StopCoroutine(_typewriter);
            // show full text immediately — caller must call Show again or Close
        }

        public void Close()
        {
            IsActive = false;
            dialoguePanel.SetActive(false);
        }
    }
}
