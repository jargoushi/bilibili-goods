type MetricCardProps = {
  label: string;
  value: string;
  hint: string;
};

export function MetricCard({ label, value, hint }: MetricCardProps) {
  return (
    // 这是首页顶部那三张“指标卡”。
    // 如果你后面想改成 4 张、6 张，通常只需要改 home-dashboard.tsx 里的 metrics 数组。
    <div className="panel-surface rounded-[24px] p-5">
      <p className="text-sm uppercase tracking-[0.28em] text-ink-2">{label}</p>
      <p className="mono-font mt-3 text-3xl font-semibold text-white">{value}</p>
      <p className="mt-3 text-sm leading-6 text-ink-1">{hint}</p>
    </div>
  );
}
