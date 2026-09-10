// Synthesize a whole text with AVSpeechSynthesizer (natural prosody) and
// record when each character range starts, so callers can map sentences
// to audio time without splitting the text.
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
let delegate = Delegate(text: text)
synth.delegate = delegate

let utt = AVSpeechUtterance(string: text)
utt.voice = voice
utt.rate = rate

var file: AVAudioFile? = nil
var finished = false

synth.write(utt) { buffer in
    guard let pcm = buffer as? AVAudioPCMBuffer else { return }
    if pcm.frameLength == 0 { finished = true; return }
    if file == nil {
        delegate.sampleRate = pcm.format.sampleRate
        var settings = pcm.format.settings
        settings[AVFormatIDKey] = kAudioFormatLinearPCM
        settings[AVLinearPCMBitDepthKey] = 16
        settings[AVLinearPCMIsFloatKey] = false
        settings[AVLinearPCMIsNonInterleaved] = false
        file = try! AVAudioFile(forWriting: outWav, settings: settings)
    }
    try! file!.write(from: pcm)
    delegate.framesWritten += Int64(pcm.frameLength)
}

// Pump the run loop until synthesis completes.
let deadline = Date().addingTimeInterval(600)
while !(finished || delegate.done) && Date() < deadline {
    RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.05))
}
// Let trailing callbacks land.
RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.3))
file = nil

let duration = delegate.sampleRate > 0 ? Double(delegate.framesWritten) / delegate.sampleRate : 0
let out: [String: Any] = [
    "sampleRate": delegate.sampleRate,
    "duration": (duration * 1000).rounded() / 1000,
    "marks": delegate.marks,
]
let data = try! JSONSerialization.data(withJSONObject: out, options: [])
try! data.write(to: outJson)
print("ok frames=\(delegate.framesWritten) sr=\(delegate.sampleRate) dur=\(String(format: "%.2f", duration))s marks=\(delegate.marks.count)")
