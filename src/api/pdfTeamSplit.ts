export type PdfTeamSplitPayload = {
  roster: File
  pdf: File
  sheet?: number | string
  nameColumn?: string
  teamColumn?: string
  fuzzyThreshold?: number | string
}

const parseErrorPayload = async (response: Response): Promise<string> => {
  let message = 'PDF 行程整理失败'

  try {
    const payload = await response.json()
    message = payload?.message ?? payload?.detail ?? message
  } catch {
    // ignore parsing errors
  }

  return message
}

export const requestPdfTeamSplit = async (payload: FormData): Promise<Blob> => {
  const response = await fetch('/api/pdf-team-split', {
    method: 'POST',
    body: payload,
  })

  if (!response.ok) {
    const message = await parseErrorPayload(response)
    throw new Error(message)
  }

  return response.blob()
}

export const downloadPdfTeamSplitResult = (blob: Blob, filename?: string) => {
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename ?? 'pdf-team-split-result.zip'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(objectUrl)
}
