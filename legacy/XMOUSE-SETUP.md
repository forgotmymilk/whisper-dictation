# X-Mouse Button Control Quick Setup

## Step 1: Download and Install X-Mouse
https://www.highrez.co.uk/downloads/xmousebuttoncontrol.htm

## Step 2: Configure Your Mouse Button

1. Open **X-Mouse Button Control**
2. Select **Global** profile (or specific app)
3. Click the mouse button you want to use (e.g., Mouse Button 4/5, or a key)
4. Select **"Simulated Keys"**

## Step 3: Enter Hotkey

In the "Simulated Keys" window:

**For push-to-talk behavior:**
```
{F15}
```

**Settings:**
- How to send the keys: **"Pressed"**
- ✓ Check "Block original mouse input"

Click **OK**

## Step 4: Test

1. Click **Apply** in X-Mouse
2. Hold your configured mouse button → Red dot appears in dictation window → Speak → Release → Text types

## Alternative Hotkeys

If F15 doesn't work, edit `config.json`:

```json
{
  "hotkey": "f16"
}
```

Then in X-Mouse, use: `{F16}`

**Recommended X-Mouse keys:**
- F15, F16, F17, F18, F19, F20 (best - never conflicts)

## Example: Side Mouse Button to F15

```
Mouse Button 4 → Simulated Keys: {F15} → Mode: Pressed
Mouse Button 5 → Simulated Keys: {F16} → Mode: Pressed
```

## Tips

- Use **"Pressed"** mode for push-to-talk (hold to record, release to stop)
- Use **"Pressed and released"** mode for toggle (click to start, click to stop)
- The dictation window shows "🔴 Recording..." when active

## Troubleshooting

**X-Mouse not working:**
- Run X-Mouse as Administrator
- Check "Show layer options" → Ensure correct layer is active

**Hotkey conflicts:**
- Try F16, F17, F18, F19, or F20 instead
- These keys exist virtually and won't conflict with any apps

**Dictation not starting:**
1. Check dictation.py is running (green text shows "Ready!")
2. Verify config.json has matching hotkey
3. Test with keyboard first (press F15 on keyboard)
4. Then configure X-Mouse
