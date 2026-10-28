import type { MascotMood } from '@/components/Mascot'

/** Picks Pip's mood and a message for a quiz percentage. */
export function moodForScore(percentage: number): { mood: MascotMood; message: string } {
  if (percentage === 100) return { mood: 'celebrating', message: 'PERFECT! Every single answer right. I am doing a happy dance!' }
  if (percentage >= 80) return { mood: 'happy', message: 'Fantastic work! You really know this stuff.' }
  if (percentage >= 60) return { mood: 'encouraging', message: 'Good effort! A quick look at the lessons below and you will ace it next time.' }
  if (percentage >= 40) return { mood: 'confused', message: 'Hmm, some of these were tricky. Review the lessons I picked out for you, then try again.' }
  return { mood: 'sad', message: 'Oh no... this one was tough. That is okay! Read the lessons below, then come back stronger.' }
}

/** Picks Pip's reaction to a failed code run, based on the error text. */
export function moodForError(stderr: string, timedOut = false): { mood: MascotMood; message: string } {
  if (timedOut) return { mood: 'confused', message: 'It ran for too long. Is there a loop that never ends?' }
  const last = stderr.trim().split('\n').pop() ?? ''
  if (/SyntaxError|IndentationError/.test(last)) return { mood: 'thinking', message: 'Python could not read that line. Check colons, brackets, quotes and indentation.' }
  if (/NameError/.test(last)) return { mood: 'thinking', message: 'A name is not defined. Did you spell the variable or function correctly?' }
  if (/TypeError/.test(last)) return { mood: 'confused', message: 'Mixing types? Check that numbers and text are converted properly.' }
  if (/ZeroDivisionError/.test(last)) return { mood: 'sad', message: 'Oops, dividing by zero is not allowed. Add a check before dividing.' }
  if (/IndexError|KeyError/.test(last)) return { mood: 'thinking', message: 'That position or key does not exist. Check the length or use .get().' }
  if (/ValueError/.test(last)) return { mood: 'confused', message: 'The value has the right type but cannot be used. Check your conversions.' }
  return { mood: 'encouraging', message: 'An error! Every programmer sees them. Read the last line of the message for the clue.' }
}
