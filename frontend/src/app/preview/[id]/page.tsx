import { ClientPreview } from "./ClientPreview";

export default async function PreviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <ClientPreview cvId={id} />;
}
