import React, { useEffect } from "react";
import { Show } from "../types";
import { formatAgeRange } from "../utils/format";
import styles from "./ShowDetailModal.module.css";

interface ShowDetailModalProps {
  show: Show | null;
  onClose: () => void;
}

export const ShowDetailModal: React.FC<ShowDetailModalProps> = ({
  show,
  onClose,
}) => {
  // Close on Escape key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  if (!show) return null;

  const stimLevel = show.stimulationLevel || "Medium"; // Default

  // Helper for stimulation badge style
  const stimStyle = {
    Low: { bg: "#E8F5E9", color: "#2E7D32", text: "🍃 Low Stimulation" },
    Medium: { bg: "#FFF3E0", color: "#E65100", text: "⚡ Medium Stimulation" },
    High: { bg: "#F3E5F5", color: "#7B1FA2", text: "🚀 High Stimulation" },
  }[stimLevel];

  const platformLogos: Record<
    string,
    { name: string; file: string }
  > = {
    netflix: { name: "Netflix", file: "/assets/providers/netflix.png" },
    disneyplus: { name: "Disney+", file: "/assets/providers/disneyplus.png" },
    hulu: { name: "Hulu", file: "/assets/providers/hulu.png" },
    primevideo: { name: "Prime Video", file: "/assets/providers/primevideo.png" },
    hbomax: { name: "HBO Max", file: "/assets/providers/hbomax.png" },
    peacock: { name: "Peacock", file: "/assets/providers/peacock.png" },
    appletv: { name: "Apple TV+", file: "/assets/providers/appletv.png" },
    paramountplus: {
      name: "Paramount+",
      file: "/assets/providers/paramountplus.png",
    },
    youtubekids: {
      name: "YouTube Kids",
      file: "/assets/providers/youtubekids.png",
    },
    roku: { name: "Roku Channel", file: "/assets/providers/roku.png" },
    tubi: { name: "Tubi", file: "/assets/providers/tubi.png" },
    plutotv: { name: "Pluto TV", file: "/assets/providers/plutotv.png" },
    sling: { name: "Sling TV", file: "/assets/providers/sling.png" },
    crunchyroll: {
      name: "Crunchyroll",
      file: "/assets/providers/crunchyroll.png",
    },
    funimation: {
      name: "Funimation",
      file: "/assets/providers/funimation.png",
    },
    noggin: { name: "Noggin", file: "/assets/providers/noggin.png" },
    pbskids: { name: "PBS Kids", file: "/assets/providers/pbskids.png" },
    nickjr: { name: "Nick Jr.", file: "/assets/providers/nickjr.png" },
    cartoonnetwork: {
      name: "Cartoon Network",
      file: "/assets/providers/cartoonnetwork.png",
    },
    disneyjunior: {
      name: "Disney Junior",
      file: "/assets/providers/disneyjunior.png",
    },
    boomerang: {
      name: "Boomerang",
      file: "/assets/providers/boomerang.png",
    },
    discoveryplus: {
      name: "Discovery+",
      file: "/assets/providers/discoveryplus.png",
    },
    kidoodle: { name: "Kidoodle.TV", file: "/assets/providers/kidoodle.png" },
    vudu: { name: "Vudu Kids", file: "/assets/providers/vudu.png" },
    xumo: { name: "Xumo", file: "/assets/providers/xumo.png" },
    kanopy: { name: "Kanopy Kids", file: "/assets/providers/kanopy.png" },
    shoutfactory: {
      name: "Shout! Factory TV",
      file: "/assets/providers/shoutfactory.png",
    },
    sundancenow: {
      name: "Sundance Now",
      file: "/assets/providers/sundancenow.png",
    },
    freevee: { name: "Freevee", file: "/assets/providers/freevee.png" },
    yippee: { name: "Yippee TV", file: "/assets/providers/yippee.png" },
    happykids: {
      name: "HappyKids TV",
      file: "/assets/providers/happykids.png",
    },
    hopster: { name: "Hopster", file: "/assets/providers/hopster.png" },
    sesameworkshop: {
      name: "Sesame Workshop",
      file: "/assets/providers/sesameworkshop.png",
    },
    pbs: { name: "PBS", file: "/assets/providers/pbs.png" },
    familyjr: {
      name: "FAMILY Jr.",
      file: "/assets/providers/familyjr.png",
    },
    retrotv: { name: "RetroTV", file: "/assets/providers/retrotv.png" },
    tinypop: { name: "Tiny Pop", file: "/assets/providers/tinypop.png" },
    babytv: { name: "BabyTV", file: "/assets/providers/babytv.png" },
    toongoggles: {
      name: "Toon Goggles",
      file: "/assets/providers/toongoggles.png",
    },
    kidzbop: { name: "Kidz Bop TV", file: "/assets/providers/kidzbop.png" },
    wildbrain: {
      name: "WildBrain TV",
      file: "/assets/providers/wildbrain.png",
    },
    nicktoons: { name: "Nicktoons", file: "/assets/providers/nicktoons.png" },
    discoveryfamily: {
      name: "Discovery Family",
      file: "/assets/providers/discoveryfamily.png",
    },
    cartoonito: {
      name: "Cartoonito",
      file: "/assets/providers/cartoonito.png",
    },
    cbs: { name: "CBS", file: "/assets/providers/cbs.png" },
  };

  const platformAliases: Record<string, string> = {
    "amazonprimevideo": "primevideo",
    "primevideo": "primevideo",
    "amazonprime": "primevideo",
    "prime": "primevideo",
    "hbo max": "hbomax",
    "hbomax": "hbomax",
    "max": "hbomax",
    "paramount plus": "paramountplus",
    "paramount+": "paramountplus",
    "cbs all access": "paramountplus",
    "imdbtv": "freevee",
    "imdb tv": "freevee",
    "disney plus": "disneyplus",
    "disney+": "disneyplus",
    "disney+ kids zone": "disneyplus",
    "peacock kids": "peacock",
    "hbo family on max": "hbomax",
    "youtube kids": "youtubekids",
    "the roku channel": "roku",
    "pbs kids": "pbskids",
    "cartoon network app": "cartoonnetwork",
    "nick jr": "nickjr",
    "nick jr.": "nickjr",
    "discovery family": "discoveryfamily",
    "sesame workshop on pbs kids": "sesameworkshop",
    "pbs passport": "pbs",
    "family jr.": "familyjr",
    "family jr": "familyjr",
    "retro tv kids blocks": "retrotv",
    "tiny pop": "tinypop",
    "cbs kids": "cbs",
  };

  const normalizePlatform = (platform: string) =>
    platform.trim().toLowerCase().replace(/[^a-z0-9+ ]/g, "");

  const resolvePlatform = (platform: string) => {
    const normalized = normalizePlatform(platform);
    const alias = platformAliases[normalized] || normalized.replace(/\s+/g, "");
    return platformLogos[alias];
  };

  const platforms =
    show.platforms && show.platforms.length > 0
      ? show.platforms
      : ["YouTube Kids"];

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>
          ×
        </button>

        <div className={styles.header}>
          <img
            src={show.coverImage}
            alt={show.title}
            className={styles.coverImage}
          />

          <div className={styles.headerInfo}>
            <div className={styles.badges}>
              <span
                className={`${styles.ratingBadge} ${show.rating === "Safe" ? styles.safe : styles.caution}`}
              >
                {show.rating === "Safe"
                  ? "✅ Safe"
                  : show.rating === "Unsafe"
                    ? "🚫 Unsafe"
                    : "⚠️ Caution"}
              </span>
              <span className={styles.ageBadge}>
                {formatAgeRange(show.minAge, show.maxAge)}
              </span>

              <span
                className={styles.stimBadge}
                style={{
                  backgroundColor: stimStyle.bg,
                  color: stimStyle.color,
                }}
              >
                {stimStyle.text}
              </span>
            </div>

            <div className={styles.titleGroup}>
              <h2 className={styles.title}>{show.title}</h2>
              <span className={styles.year}>
                {show.releaseYear && show.releaseYear}
                {show.releaseYear && show.runtime && " • "}
                {show.runtime && show.runtime}
              </span>
            </div>

            <div className={styles.tags}>
              {show.tags.map((tag) => (
                <span key={tag} className={styles.tag}>
                  {tag}
                </span>
              ))}
            </div>

            {platforms.length > 0 && (
              <div className={styles.platforms}>
                <span className={styles.platformsLabel}>Watch on</span>
                <div className={styles.platformsList}>
                  {platforms.map((platform) => {
                    const meta = resolvePlatform(platform);
                    if (!meta) {
                      return null;
                    }

                    return (
                      <span
                        key={`${platform}-${meta.name}`}
                        className={styles.platformChip}
                        aria-label={`${meta.name} logo`}
                      >
                        <img
                          className={styles.platformLogo}
                          src={meta.file}
                          alt={`${meta.name} logo`}
                          loading="lazy"
                        />
                      </span>
                    );
                  })}
                </div>
              </div>
            )}

            <p className={styles.synopsis}>{show.synopsis}</p>
          </div>
        </div>

        <div className={styles.body}>
          <div className={styles.section}>
            <h3>🎭 Cast</h3>
            <div className={styles.castList}>
              {show.cast.length > 0 ? (
                show.cast.map((actor) => (
                  <span key={actor} className={styles.castMember}>
                    {actor}
                  </span>
                ))
              ) : (
                <span className={styles.placeholder}>
                  No cast info available.
                </span>
              )}
            </div>
          </div>

          <div className={styles.section}>
            <h3>🛡️ Safety Assessment</h3>
            <div className={styles.reasoningBox}>{show.reasoning}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
