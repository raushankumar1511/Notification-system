export type Channel = "whatsapp" | "email" | "webpush";

export const CHANNELS: Channel[] = ["whatsapp", "email", "webpush"];

export const CHANNEL_LABELS: Record<Channel, string> = {
  whatsapp: "WhatsApp",
  email: "Email",
  webpush: "Web Push",
};

export interface User {
  id: number;
  email: string;
  username: string;
  phone_number: string;
  is_staff: boolean;
  last_seen: string | null;
}

export interface Template {
  id: number;
  trigger: number;
  channel: Channel;
  is_enabled: boolean;
  subject: string;
  title: string;
  body: string;
  provider_config: Record<string, unknown>;
  variables: Record<string, string>;
  updated_at: string;
}

export interface Trigger {
  id: number;
  slug: string;
  name: string;
  description: string;
  event_type: "EVENT" | "SCHEDULED";
  schedule_config: Record<string, unknown>;
  is_active: boolean;
  templates: Template[];
}

export interface NotificationLog {
  id: number;
  user: number | null;
  template: number | null;
  trigger_slug: string;
  channel: Channel;
  recipient: string;
  status: "sent" | "failed" | "skipped";
  is_test: boolean;
  provider_message_id: string;
  error: string;
  created_at: string;
}
