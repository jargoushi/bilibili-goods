import { HomeDashboard } from "@/components/console/home-dashboard";

export default function Home() {
  // 首页本身不放复杂逻辑，只做路由入口。
  // 真正的页面结构放到 components/console 中，后续更容易拆分维护。
  return <HomeDashboard />;
}
