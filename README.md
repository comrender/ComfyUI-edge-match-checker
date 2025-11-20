How to use it in your workflow?
Input two similar image masks or two similar images and remove background with node like RMBG and provide output as alpha image mask.
Node will compare two image masks if they are slightly differ the answer will be No, if they match 95%(can be adjusted) + the answer will be Yes.

Why ?
Its suitable to automatically comparing images after image editing models for minor shifts and missmatches in proportions, since its crucial for production.

Suggested min_overlap_percent 95

Output can be connected with Boolean logic to decide for the next steps.
