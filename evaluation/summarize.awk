BEGIN {
  FS = " \\| ";
  file = ARGV[1];
}

/^Scopes\(cue match\):/ {
  sp = $6; sr = $7;
}

/^Scope tokens\(no cue match\):/ {
  tp = $6; tr = $7;
}


/^Negated\(no cue match\):/ {
  ep = $6; er = $7;
}


/^Full negation:/ {
  np = $6; nr = $7;
}

END {
  printf("%s\t%s\t%s\t\t%s\t%s\t\t%s\t%s\t\t%s\t%s\n", file, sp, sr, tp, tr, ep, er, np, nr);
}
