import React, { useState, useEffect, useCallback } from "react";
import { Sidebar, NAV_ITEMS } from "./components/Sidebar";
import { Header } from "./components/Header";
import { FilterBar } from "./components/FilterBar";
import { OverviewPage } from "./pages/OverviewPage";
import { ArrivalsPage } from "./pages/ArrivalsPage";
import { PricesPage } from "./pages/PricesPage";
import { WeatherPage } from "./pages/WeatherPage";
import { TransportPage } from "./pages/TransportPage";
import { RiskPage } from "./pages/RiskPage";
import { AssistantPage } from "./pages/AssistantPage";
import { SettingsPage } from "./pages/SettingsPage";
import { api } from "./api/client";
import { AnimatePresence, motion } from "framer-motion";

export function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filterOptions, setFilterOptions] = useState(null);
  const [selectedFilters, setSelectedFilters] = useState({
    states: [],
    districts: [],
    mandis: [],
    crops: [],
    startDate: "",
    endDate: "",
  });

  const [pageData, setPageData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedRiskCrop, setSelectedRiskCrop] = useState(null);
  const [health, setHealth] = useState(null);

  // Load filter options and health on mount
  useEffect(() => {
    api
      .getFilters()
      .then((opts) => {
        setFilterOptions(opts);
        setSelectedFilters((prev) => ({
          ...prev,
          startDate: opts.date_range?.min || "",
          endDate: opts.date_range?.max || "",
        }));
      })
      .catch((err) => console.error("Failed to load filter options:", err));

    api
      .getHealth()
      .then((h) => setHealth(h))
      .catch((err) => console.error("Health check error:", err));
  }, []);

  // Fetch page data on tab or filter changes
  const loadPageData = useCallback(async () => {
    if (activeTab === "assistant" || activeTab === "settings") {
      setPageData(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      let data = null;
      if (activeTab === "overview") {
        data = await api.getOverview(selectedFilters);
      } else if (activeTab === "arrivals") {
        data = await api.getArrivals(selectedFilters);
      } else if (activeTab === "prices") {
        data = await api.getPrices(selectedFilters);
      } else if (activeTab === "weather") {
        data = await api.getWeather();
      } else if (activeTab === "transport") {
        data = await api.getTransport();
      } else if (activeTab === "risk") {
        data = await api.getRisk(selectedRiskCrop);
      }
      setPageData(data);
    } catch (err) {
      console.error(`Error loading data for ${activeTab}:`, err);
      setError(err.message || "Failed to load dashboard metrics.");
    } finally {
      setIsLoading(false);
    }
  }, [activeTab, selectedFilters, selectedRiskCrop]);

  useEffect(() => {
    loadPageData();
  }, [loadPageData]);

  const handleResetFilters = () => {
    if (filterOptions) {
      setSelectedFilters({
        states: [],
        districts: [],
        mandis: [],
        crops: [],
        startDate: filterOptions.date_range?.min || "",
        endDate: filterOptions.date_range?.max || "",
      });
    }
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case "overview":
        return (
          <OverviewPage
            data={pageData}
            isLoading={isLoading}
            error={error}
            onRetry={loadPageData}
          />
        );
      case "arrivals":
        return (
          <ArrivalsPage
            data={pageData}
            isLoading={isLoading}
            error={error}
            onRetry={loadPageData}
          />
        );
      case "prices":
        return (
          <PricesPage
            data={pageData}
            isLoading={isLoading}
            error={error}
            onRetry={loadPageData}
          />
        );
      case "weather":
        return (
          <WeatherPage
            data={pageData}
            isLoading={isLoading}
            error={error}
            onRetry={loadPageData}
          />
        );
      case "transport":
        return (
          <TransportPage
            data={pageData}
            isLoading={isLoading}
            error={error}
            onRetry={loadPageData}
          />
        );
      case "risk":
        return (
          <RiskPage
            data={pageData}
            isLoading={isLoading}
            error={error}
            onCropChange={(c) => setSelectedRiskCrop(c)}
            onRetry={loadPageData}
          />
        );
      case "assistant":
        return <AssistantPage />;
      case "settings":
        return <SettingsPage />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex">
      {/* Fixed Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          isSidebarCollapsed ? "pl-20" : "pl-64"
        }`}
      >
        {/* Top Header */}
        <Header
          activeTab={activeTab}
          navItems={NAV_ITEMS}
          onRefresh={loadPageData}
          isLoading={isLoading}
          showFilters={showFilters}
          setShowFilters={setShowFilters}
          onOpenAssistant={() => setActiveTab("assistant")}
          health={health}
        />

        {/* Global Filter Bar Drawer */}
        <AnimatePresence>
          {showFilters && activeTab !== "assistant" && activeTab !== "settings" && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.25 }}
              className="overflow-hidden"
            >
              <FilterBar
                filterOptions={filterOptions}
                selectedFilters={selectedFilters}
                onFilterChange={setSelectedFilters}
                onResetFilters={handleResetFilters}
                onClose={() => setShowFilters(false)}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Page Content View */}
        <main className="flex-1 p-6 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              {renderActivePage()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

export default App;
