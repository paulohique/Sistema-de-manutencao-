export type GlpiOpenTicketItem = {
  id: number;
  title: string;
};

export type GlpiOpenTicketsResponse = {
  items: GlpiOpenTicketItem[];
  total: number;
};
