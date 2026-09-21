import React from "react";
import { X, RotateCcw, Check, Calendar, MapPin, Sprout, Building2 } from "lucide-react";

export function FilterBar({
  filterOptions,
  selectedFilters,
  onFilterChange,
  onResetFilters,
  onClose,
}) {
  const { states = [], districts = [], mandis = [], crops = [], date_range = {} } =
    filterOptions || {};

  // Filter districts based on selected states
  const availableDistricts = districts.filter((d) => {
    if (!selectedFilters.states.length) return true;
    const matchingMandis = mandis.filter((m) => selectedFilters.states.includes(m.state));
    return matchingMandis.some((m) => m.district === d);
  });

  // Filter mandis based on selected states & districts
  const availableMandis = mandis.filter((m) => {
    if (selectedFilters.states.length && !selectedFilters.states.includes(m.state)) return false;
    if (selectedFilters.districts.length && !selectedFilters.districts.includes(m.district))
      return false;
    return true;
  });

  const handleMultiToggle = (key, value) => {
    const current = selectedFilters[key] || [];
    const updated = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    onFilterChange({ ...selectedFilters, [key]: updated });
  };

  const handleSelectAll = (key, allValues) => {
    onFilterChange({ ...selectedFilters, [key]: allValues });
  };

  const handleClear = (key) => {
    onFilterChange({ ...selectedFilters, [key]: [] });
  };

  const activeCount =
    (selectedFilters.states.length ? 1 : 0) +
    (selectedFilters.districts.length ? 1 : 0) +
    (selectedFilters.mandis.length ? 1 : 0) +
    (selectedFilters.crops.length ? 1 : 0) +
    (selectedFilters.startDate ? 1 : 0) +
    (selectedFilters.endDate ? 1 : 0);

  return (
    <div className="bg-slate-900/95 border-b border-slate-800 px-6 py-4 shadow-glass transition-all">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-white">Global Filters</span>
          {activeCount > 0 && (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              {activeCount} Active
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onResetFilters}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-emerald-400 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset All</span>
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* 1. State Filter */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs text-slate-300 font-medium">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-emerald-400" />
              State ({selectedFilters.states.length || "All"})
            </span>
            <div className="text-[10px] space-x-1">
              <button
                onClick={() => handleSelectAll("states", states)}
                className="text-emerald-400 hover:underline"
              >
                All
              </button>
              <span className="text-slate-600">|</span>
              <button onClick={() => handleClear("states")} className="text-slate-400 hover:underline">
                Clear
              </button>
            </div>
          </div>
          <div className="max-h-28 overflow-y-auto rounded-lg bg-slate-950 p-1.5 border border-slate-800 space-y-0.5 text-xs">
            {states.map((st) => {
              const isSelected = selectedFilters.states.includes(st);
              return (
                <button
                  key={st}
                  onClick={() => handleMultiToggle("states", st)}
                  className={`w-full flex items-center justify-between px-2 py-1 rounded text-left transition-colors ${
                    isSelected
                      ? "bg-emerald-600/30 text-emerald-200 font-medium"
                      : "text-slate-400 hover:bg-slate-850 hover:text-slate-200"
                  }`}
                >
                  <span className="truncate">{st}</span>
                  {isSelected && <Check className="w-3 h-3 text-emerald-400 flex-shrink-0" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* 2. District Filter */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs text-slate-300 font-medium">
            <span className="flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5 text-emerald-400" />
              District ({selectedFilters.districts.length || "All"})
            </span>
            <div className="text-[10px] space-x-1">
              <button
                onClick={() => handleSelectAll("districts", availableDistricts)}
                className="text-emerald-400 hover:underline"
              >
                All
              </button>
              <span className="text-slate-600">|</span>
              <button onClick={() => handleClear("districts")} className="text-slate-400 hover:underline">
                Clear
              </button>
            </div>
          </div>
          <div className="max-h-28 overflow-y-auto rounded-lg bg-slate-950 p-1.5 border border-slate-800 space-y-0.5 text-xs">
            {availableDistricts.map((dst) => {
              const isSelected = selectedFilters.districts.includes(dst);
              return (
                <button
                  key={dst}
                  onClick={() => handleMultiToggle("districts", dst)}
                  className={`w-full flex items-center justify-between px-2 py-1 rounded text-left transition-colors ${
                    isSelected
                      ? "bg-emerald-600/30 text-emerald-200 font-medium"
                      : "text-slate-400 hover:bg-slate-850 hover:text-slate-200"
                  }`}
                >
                  <span className="truncate">{dst}</span>
                  {isSelected && <Check className="w-3 h-3 text-emerald-400 flex-shrink-0" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* 3. Mandi Filter */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs text-slate-300 font-medium">
            <span className="flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5 text-emerald-400" />
              Mandi ({selectedFilters.mandis.length || "All"})
            </span>
            <div className="text-[10px] space-x-1">
              <button
                onClick={() =>
                  handleSelectAll(
                    "mandis",
                    availableMandis.map((m) => m.mandi_id)
                  )
                }
                className="text-emerald-400 hover:underline"
              >
                All
              </button>
              <span className="text-slate-600">|</span>
              <button onClick={() => handleClear("mandis")} className="text-slate-400 hover:underline">
                Clear
              </button>
            </div>
          </div>
          <div className="max-h-28 overflow-y-auto rounded-lg bg-slate-950 p-1.5 border border-slate-800 space-y-0.5 text-xs">
            {availableMandis.map((m) => {
              const isSelected = selectedFilters.mandis.includes(m.mandi_id);
              return (
                <button
                  key={m.mandi_id}
                  onClick={() => handleMultiToggle("mandis", m.mandi_id)}
                  className={`w-full flex items-center justify-between px-2 py-1 rounded text-left transition-colors ${
                    isSelected
                      ? "bg-emerald-600/30 text-emerald-200 font-medium"
                      : "text-slate-400 hover:bg-slate-850 hover:text-slate-200"
                  }`}
                >
                  <span className="truncate">{m.mandi_name}</span>
                  {isSelected && <Check className="w-3 h-3 text-emerald-400 flex-shrink-0" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* 4. Crop Filter */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs text-slate-300 font-medium">
            <span className="flex items-center gap-1">
              <Sprout className="w-3.5 h-3.5 text-emerald-400" />
              Crop ({selectedFilters.crops.length || "All"})
            </span>
            <div className="text-[10px] space-x-1">
              <button
                onClick={() => handleSelectAll("crops", crops)}
                className="text-emerald-400 hover:underline"
              >
                All
              </button>
              <span className="text-slate-600">|</span>
              <button onClick={() => handleClear("crops")} className="text-slate-400 hover:underline">
                Clear
              </button>
            </div>
          </div>
          <div className="max-h-28 overflow-y-auto rounded-lg bg-slate-950 p-1.5 border border-slate-800 space-y-0.5 text-xs">
            {crops.map((c) => {
              const isSelected = selectedFilters.crops.includes(c);
              return (
                <button
                  key={c}
                  onClick={() => handleMultiToggle("crops", c)}
                  className={`w-full flex items-center justify-between px-2 py-1 rounded text-left transition-colors ${
                    isSelected
                      ? "bg-emerald-600/30 text-emerald-200 font-medium"
                      : "text-slate-400 hover:bg-slate-850 hover:text-slate-200"
                  }`}
                >
                  <span className="truncate">{c}</span>
                  {isSelected && <Check className="w-3 h-3 text-emerald-400 flex-shrink-0" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* 5. Date Range Filter */}
        <div className="space-y-1.5">
          <div className="text-xs text-slate-300 font-medium flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-emerald-400" />
            <span>Date Range</span>
          </div>
          <div className="space-y-2 text-xs">
            <div>
              <label className="block text-[10px] text-slate-400 mb-0.5">Start Date</label>
              <input
                type="date"
                min={date_range.min}
                max={date_range.max}
                value={selectedFilters.startDate || date_range.min || ""}
                onChange={(e) =>
                  onFilterChange({ ...selectedFilters, startDate: e.target.value })
                }
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:border-emerald-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[10px] text-slate-400 mb-0.5">End Date</label>
              <input
                type="date"
                min={date_range.min}
                max={date_range.max}
                value={selectedFilters.endDate || date_range.max || ""}
                onChange={(e) =>
                  onFilterChange({ ...selectedFilters, endDate: e.target.value })
                }
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:border-emerald-500 focus:outline-none"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
