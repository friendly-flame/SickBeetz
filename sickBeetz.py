import sys
import librosa
import segmentr
import klassifier
import reconstructor
import os

import sick_beetz_gui


def main(file_path, kit):
    y, sr = librosa.load(file_path, sr=None)
    segments = segmentr.segment_audio(y, sr)
    samples = [s[0] for s in segments]
    times = [s[1] for s in segments]

    # build the KNN classifier
    model = klassifier.load_classifier()
    replacements = []
    ssr = 0
    for seg in samples:
        sy, ssr = klassifier.use_classifier(model, seg, kit)
        replacements.append(sy)

    # quantize and reconstruct
    quantized_times = quantize_times(y, sr, times)
    output = reconstructor.replace(quantized_times, replacements, ssr)
    librosa.output.write_wav('output.wav', output, ssr)


def quantize_times(y, sr, times):
    result = []
    tempo, beats = librosa.beat.beat_track(y, sr)
    print 'old tempo: ', tempo
    while tempo > 220:
        tempo = tempo/2
    while tempo < 90:
        tempo = tempo*2
    print 'new tempo: ', tempo
    beet = 16/tempo
    print 'old times: ', times
    first_time = times[0]
    for time in times:
        time = time - first_time
        time = beet*round(float(time)/beet)
        time = time + first_time
        result.append(time)
    print 'new times: ', result
    return result


def relative_path(path):
    """
    Get file path relative to calling script's directory
    :param path: filename or file path
    :return: full path name, relative to script location
    """
    return os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), path)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sick_beetz_gui.main()
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print 'usage: python sickBeetz [path_to_wav] [kit]'