import React from "react";
import Link from "next/link";
import { Order } from "@/lib/types";
import { Card, CardHeader } from "../ui/Card";
import {
  TableContainer,
  Table,
  TableHead,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
} from "../ui/Table";
import { RiskBadge } from "../risk/RiskBadge";
import { PolicyBadge } from "../policies/PolicyBadge";
import { ChevronRightIcon } from "../ui/Icons";

export interface DecisionTableProps {
  orders: Order[];
  className?: string;
}

export function DecisionTable({ orders, className = "" }: DecisionTableProps) {
  return (
    <Card className={className}>
      <CardHeader
        title="Recent AI Decisions"
        subtitle="Automated checkout intercept & policy routing logs"
        action={
          <Link
            href="/orders"
            className="text-xs font-medium text-[var(--accent)] hover:underline inline-flex items-center gap-1"
          >
            View all orders
            <ChevronRightIcon size={14} />
          </Link>
        }
      />

      <TableContainer className="border-0 rounded-none">
        <Table>
          <TableHead>
            <tr>
              <TableHeaderCell>Order ID</TableHeaderCell>
              <TableHeaderCell>Customer</TableHeaderCell>
              <TableHeaderCell>Cart Value</TableHeaderCell>
              <TableHeaderCell>Risk Assessment</TableHeaderCell>
              <TableHeaderCell>Assigned Policy</TableHeaderCell>
              <TableHeaderCell>Confidence</TableHeaderCell>
              <TableHeaderCell className="text-right">Action</TableHeaderCell>
            </tr>
          </TableHead>
          <TableBody>
            {orders.slice(0, 5).map((order) => (
              <TableRow key={order.id}>
                <TableCell mono className="font-medium text-[var(--accent)]">
                  <Link href={`/risk-analysis?orderId=${order.id}`} className="hover:underline">
                    {order.id}
                  </Link>
                </TableCell>

                <TableCell>
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-center text-[10px] font-medium text-[var(--ink-900)]">
                      {order.customer.avatarInitials}
                    </div>
                    <span className="font-medium text-[var(--ink-900)] truncate max-w-[140px]">
                      {order.customer.name}
                    </span>
                  </div>
                </TableCell>

                <TableCell mono>
                  {order.currency}
                  {order.cartValue.toLocaleString("en-IN")}
                </TableCell>

                <TableCell>
                  <div className="flex items-center gap-2">
                    <RiskBadge level={order.riskLevel} size="sm" />
                    <span className="font-mono text-xs text-[var(--ink-400)] tabular-nums">
                      ({order.riskScore}/100)
                    </span>
                  </div>
                </TableCell>

                <TableCell>
                  <PolicyBadge policy={order.policy} size="sm" />
                </TableCell>

                <TableCell mono>
                  <span className="font-medium">{order.confidence}%</span>
                </TableCell>

                <TableCell className="text-right">
                  <Link
                    href={`/risk-analysis?orderId=${order.id}`}
                    className="inline-flex items-center text-xs font-medium text-[var(--ink-600)] hover:text-[var(--accent)] gap-0.5"
                  >
                    Inspect
                    <ChevronRightIcon size={12} />
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Card>
  );
}
