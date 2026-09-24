// Synthesize a whole text with AVSpeechSynthesizer (natural prosody) and
// record when each character range starts, so callers can map sentences
// to audio time without splitting the text.
//
// AVSpeechSynthesizer.write() stops emitting audio slightly before the final
// word has finished — measured at ~0.2s on "…his heirs and successors.", which
// is enough to swallow the last syllable. So a short sentinel sentence is
// appended, the audio is kept in memory, and everything from the sentinel's
// first word onward is thrown away. The real last word is then a mid-text word
// and gets rendered in full; the cut lands inside the pause after it.
// Appending the sentinel does not disturb the preceding prosody: the word marks
// before it come back bit-identical (verified 2026-09-24).
//
// Usage: tts_align <voiceIdentifier> <rate> <input.txt> <out.wav> <out.json>
//   rate: AVSpeechUtterance rate (0.5 = default)
// Output JSON: {"sampleRate":N,"duration":sec,"marks":[{"loc":charIndex,"len":n,"t":sec},...]}

import AVFoundation
import Foundation

let args = CommandLine.arguments
guard args.count == 6 else {
    FileHandle.standardError.write("usage: tts_align <voiceId> <rate> <in.txt> <out.wav> <out.json>\n".data(using: .utf8)!)
    exit(2)
}
let voiceId = args[1]
let rate = Float(args[2]) ?? 0.5
let text = try! String(contentsOfFile: args[3], encoding: .utf8)
    .trimmingCharacters(in: .whitespacesAndNewlines)
// Give the real text a sentence ending of its own first, so an isolated word
// (the dictionary clips) still gets sentence-final prosody rather than the
// rising tone of a word that leads into another sentence.
let endsSentence = text.range(of: "[.!?。！？]$", options: .regularExpression) != nil
let sentinel = (endsSentence ? " " : ". ") + "End."
let fullText = text + sentinel
let cutFromUTF16 = (text as NSString).length + (endsSentence ? 1 : 2)
let outWav = URL(fileURLWithPath: args[4])
let outJson = URL(fileURLWithPath: args[5])

guard let voice = AVSpeechSynthesisVoice(identifier: voiceId) else {
    FileHandle.standardError.write("voice not found: \(voiceId)\n".data(using: .utf8)!)
    for v in AVSpeechSynthesisVoice.speechVoices() where v.language.hasPrefix("en") || v.language.hasPrefix("zh") {
        FileHandle.standardError.write("  \(v.identifier)  \(v.language)  \(v.quality.rawValue)\n".data(using: .utf8)!)
    }
    exit(3)
}

final class Delegate: NSObject, AVSpeechSynthesizerDelegate {
    var marks: [[String: Any]] = []
    var framesWritten: Int64 = 0
    var sampleRate: Double = 0
    var done = false
    let nsText: NSString
    init(text: String) { nsText = text as NSString }

    func speechSynthesizer(_ s: AVSpeechSynthesizer, willSpeakRangeOfSpeechString r: NSRange, utterance: AVSpeechUtterance) {
        let t = sampleRate > 0 ? Double(framesWritten) / sampleRate : 0
        marks.append(["loc": r.location, "len": r.length, "t": (t * 1000).rounded() / 1000])
    }
    func speechSynthesizer(_ s: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) { done = true }
    func speechSynthesizer(_ s: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) { done = true }
}

let synth = AVSpeechSynthesizer()
let delegate = Delegate(text: fullText)
synth.delegate = delegate

let utt = AVSpeechUtterance(string: fullText)
utt.voice = voice
utt.rate = rate

var buffers: [AVAudioPCMBuffer] = []
var format: AVAudioFormat? = nil
var finished = false

synth.write(utt) { buffer in
    guard let pcm = buffer as? AVAudioPCMBuffer else { return }
    if pcm.frameLength == 0 { finished = true; return }
    if format == nil {
        format = pcm.format
        delegate.sampleRate = pcm.format.sampleRate
    }
    buffers.append(pcm)
    delegate.framesWritten += Int64(pcm.frameLength)
}

// Pump the run loop until synthesis completes.
let deadline = Date().addingTimeInterval(600)
while !(finished || delegate.done) && Date() < deadline {
    RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.05))
}
// Let trailing callbacks land.
RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.3))

// Where the sentinel starts speaking = where the real content is finished.
let realMarks = delegate.marks.filter { ($0["loc"] as! Int) < cutFromUTF16 }
let sentinelMark = delegate.marks.first { ($0["loc"] as! Int) >= cutFromUTF16 }
var cutFrames = delegate.framesWritten
if let sm = sentinelMark, delegate.sampleRate > 0 {
    cutFrames = Int64((sm["t"] as! Double) * delegate.sampleRate)
}
if cutFrames <= 0 || cutFrames > delegate.framesWritten { cutFrames = delegate.framesWritten }

if let fmt = format {
    var settings = fmt.settings
    settings[AVFormatIDKey] = kAudioFormatLinearPCM
    settings[AVLinearPCMBitDepthKey] = 16
    settings[AVLinearPCMIsFloatKey] = false
    settings[AVLinearPCMIsNonInterleaved] = false
    let file = try! AVAudioFile(forWriting: outWav, settings: settings)
    var written: Int64 = 0
    for pcm in buffers {
        if written >= cutFrames { break }
        let remain = cutFrames - written
        if Int64(pcm.frameLength) <= remain {
            try! file.write(from: pcm)
            written += Int64(pcm.frameLength)
        } else {
            pcm.frameLength = AVAudioFrameCount(remain)
            try! file.write(from: pcm)
            written = cutFrames
        }
    }
}

let duration = delegate.sampleRate > 0 ? Double(cutFrames) / delegate.sampleRate : 0
let out: [String: Any] = [
    "sampleRate": delegate.sampleRate,
    "duration": (duration * 1000).rounded() / 1000,
    "marks": realMarks,
]
let data = try! JSONSerialization.data(withJSONObject: out, options: [])
try! data.write(to: outJson)
print("ok frames=\(cutFrames)/\(delegate.framesWritten) sr=\(delegate.sampleRate) dur=\(String(format: "%.2f", duration))s marks=\(realMarks.count)")
