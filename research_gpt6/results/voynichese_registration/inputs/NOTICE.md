# Sources and changes

The four XML files retain the original Copyright (C) 2014 The Voynichese Project and Apache License 2.0 headers. They were extracted without edits from the hash-pinned original XML collection. A full copy of Apache License 2.0 accompanies them.

The `.json` files are strict JSON coordinate/data responses served at the public `/1/data/folio/script/` URLs, saved without executing them. They contain data, not the compiled browser application. Acquisition URLs and SHA-256 values are recorded separately. Voynichese documents its EVA-based transcription and spatial data release at https://github.com/voynichese/voynichese/blob/wiki/DataSets.md . Transcription contributors credited by that project include Takeshi Takahashi and Jorge Stolfi. These snapshots are used to calibrate coordinate frames; they are not independent readings.

The `.jpg` files are unchanged cropped preview photographs served by Voynichese. That project credits Yale University Library, Beinecke Rare Book and Manuscript Library, as their source: https://github.com/voynichese/voynichese/blob/wiki/CreditsAndCopyright.md . Image rights are separate from the transcription data; this notice assigns no new license to the photographs. The target Yale images were already preserved with attribution in experiment 59.

The project-derived `voynichese_registration_inputs.json` pairs the unchanged XML readings and boxes with the preview coordinate records only after checking complete equality of the reading sequence. Registration code and output polygons are new derivatives. Nonpositive-width boxes remain flagged and are not filled in. No phonetic or semantic values are assigned.
